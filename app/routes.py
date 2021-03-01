from flask import render_template, flash, redirect, url_for, request
from app import app, db
from sqlalchemy import and_
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Liked, Comment, Tagged, Collected
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, EditPostForm, CommentForm, ChangePwForm, AccForm, MdForm
from datetime import datetime
from flask_pagedown import PageDown
import os, string
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'static/uploads')
app.config['PP_PATH'] = os.path.join(app.root_path, 'static/pp')
app.config['PC_PATH'] = os.path.join(app.root_path, 'static/pc')
import uuid
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',user=current_user,posts=posts)

@app.route('/login',methods=['GET','POST'])
def login():
    #判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    #对表格数据进行验证
    if form.validate_on_submit():
        #根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        #判断用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            #如果用户不存在或者密码不正确就会闪现这条信息
            flash('无效的用户名或密码')
            #然后重定向到登录页面
            return redirect(url_for('login'))
        #这是一个非常方便的方法，当用户名和密码都正确时来解决记住用户是否记住登录状态的问题
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',title='登录',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#以下是注册表单方法
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜你成为我们网站的新用户!')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)

#以下是用户中心方法
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    collected_posts = Post.query.filter(and_(Collected.user_id==current_user.id,Post.id==Collected.post_id)).order_by(Collected.timestamp.desc()).all()
    collected_times = Collected.query.filter(Collected.user_id==current_user.id).order_by(Collected.timestamp.desc()).all()
    liked_posts = Post.query.filter(and_(Liked.user_id==current_user.id,Post.id==Liked.post_id)).order_by(Liked.timestamp.desc()).all()
    liked_times = Liked.query.filter(Liked.user_id==current_user.id).order_by(Liked.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts,collected_posts=collected_posts,collected_times=collected_times,liked_times=liked_times,liked_posts=liked_posts)

#以下服务于访问时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

#以下用于编辑个人资料
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if not form.Profile_Pic.data == None:
            pp = form.Profile_Pic.data
            filename = str(current_user.id) + '.jpg'
            pp.save(os.path.join(app.config['PP_PATH'], filename))
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('你的提交已变更.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='个人资料编辑', form=form, user=current_user)

#以下用于ACC修改个人资料
@app.route('/acc_edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def acc_edit_user(user_id):
    form = EditProfileForm()
    editing_user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        if not form.Profile_Pic.data == None:
            pp = form.Profile_Pic.data
            filename = str(editing_user.id) + '.jpg'
            pp.save(os.path.join(app.config['PP_PATH'], filename))
        editing_user.username = form.username.data
        editing_user.about_me = form.about_me.data
        db.session.commit()
        flash('你的提交已变更.')
        return redirect(url_for('acc'))
    elif request.method == 'GET':
        form.username.data = editing_user.username
        form.about_me.data = editing_user.about_me
    return render_template('edit_profile.html', title='个人资料编辑', form=form, user=editing_user)

#以下是发帖页面
@app.route('/sendpost', methods=['GET', 'POST'])
@login_required
def sendpost():
    form = PostForm()     
    if form.validate_on_submit():
        if not form.video.data == None:
            f = form.video.data
            filename = random_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            newpost = Post(user_id=current_user.id,title=form.title.data,body=form.body.data,video_id=filename)
            db.session.add(newpost)
            db.session.commit()
        else:
            newpost = Post(user_id=current_user.id,title=form.title.data,body=form.body.data,video_id=None)
            db.session.add(newpost)
            db.session.commit()
        if not form.tag.data == None:
            new_tag = Tagged(post_id=newpost.id,body=form.tag.data)
            db.session.add(new_tag)
            db.session.commit()
        c = form.cover.data
        c_filename = str(newpost.id) + '.jpg'
        c.save(os.path.join(app.config['PC_PATH'], c_filename))
        flash('你的帖子已发出.')
        return redirect(url_for('index'))
    return render_template('sendpost.html',user=current_user, form=form)

#以下是博客显示页面
@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    mdform = MdForm()
    post = Post.query.filter_by(id=post_id).first_or_404()
    mdform.body.data = post.body
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.desc()).all()
    tags = Tagged.query.filter_by(post_id=post_id).all()
    liked_cnt = Liked.query.filter_by(post_id=post_id).count()
    collected_cnt = Collected.query.filter_by(post_id=post_id).count()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(body=form.body.data,user_id=current_user.id,post_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('post', post_id=post.id))
        else:
            return redirect(url_for('login'))
    if not current_user.is_authenticated:
        isLiked = False
        isCollected = False
    else:
        if Liked.query.filter(and_(Liked.post_id==post_id,Liked.user_id==current_user.id)).count() == 0:
            isLiked = False
        else:
            isLiked = True
        if Collected.query.filter(and_(Collected.post_id==post_id,Collected.user_id==current_user.id)).count() == 0:
            isCollected = False
        else:
            isCollected = True
    return render_template('post.html',
        mdform=mdform,form=form,post=post,liked_cnt=liked_cnt,isLiked=isLiked,comments=comments,collected_cnt=collected_cnt,isCollected=isCollected,tags=tags)

#以下用于删除博客
@app.route('/deletepost/<post_id>')
@login_required
def deletepost(post_id):
    deleting_post = Post.query.get(post_id)
    if deleting_post.video_id == None:
        db.session.delete(deleting_post)
        db.session.commit()
        flash('你的帖子已删除.')
        return redirect(url_for('index'))
    else:
        os.remove(app.config['UPLOAD_PATH']+'/'+deleting_post.video_id)
        db.session.delete(deleting_post)
        db.session.commit()
        flash('你的帖子已删除.')
        return redirect(url_for('index'))

#以下用于编辑博客
@app.route('/editpost/<post_id>', methods=['GET', 'POST'])
@login_required
def editpost(post_id):
    form = EditPostForm()
    editing_post = Post.query.get(post_id)
    if form.validate_on_submit():
        if not form.cover.data == None:
            os.remove(app.config['PC_PATH']+'/'+post_id+'.jpg')
            c = form.cover.data
            c.save(os.path.join(app.config['PC_PATH']+'/'+post_id+'.jpg'))
        if editing_post.video_id:
            if form.delete_video_or_not:
                os.remove(app.config['UPLOAD_PATH']+'/'+editing_post.video_id)
                editing_post.video_id = None
            elif not form.video.data == None:
                os.remove(app.config['UPLOAD_PATH']+'/'+editing_post.video_id)
                f = form.video.data
                filename = random_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                editing_post.video_id = filename
        elif not form.video.data == None:
            f = form.video.data
            filename = random_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            editing_post.video_id = filename
        editing_post.title = form.title.data
        editing_post.body = form.body.data
        db.session.commit()
        flash('你的提交已变更.')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = editing_post.title
        form.body.data = editing_post.body
    return render_template('edit_post.html', form=form, user=current_user, post=editing_post)

#以下用于点赞博客
@app.route('/likepost/<post_id>_<user_id>')
@login_required
def likepost(post_id,user_id):
    new_like = Liked(user_id=user_id,post_id=post_id)
    db.session.add(new_like)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id,user_id=user_id))

#以下用于取消点赞
@app.route('/dislikepost/<post_id>_<user_id>')
@login_required
def dislikepost(post_id,user_id):
    disliking_id = Liked.query.filter(and_(post_id==post_id,user_id==user_id)).first_or_404().id
    disliking = Liked.query.get(disliking_id)
    db.session.delete(disliking)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id,user_id=user_id))

#以下用于删除评论
@app.route('/delcomment/<post_id>_<comment_id>')
@login_required
def delcomment(post_id,comment_id):
    deleting_comment = Comment.query.get(comment_id)
    db.session.delete(deleting_comment)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

#以下用于改密
@app.route('/changepw/<user_id>',methods=['GET', 'POST'])
@login_required
def changepw(user_id):
    changingpw_user = User.query.get(user_id)
    form = ChangePwForm()
    if form.validate_on_submit():
        if not changingpw_user.check_password(form.ori_pw.data):
            flash('旧密码不正确')
            return redirect(url_for('changepw', user_id=user_id))
        changingpw_user.set_password(form.new_pw.data)
        db.session.commit()
        flash('密码已修改')
        return redirect(url_for('user', username=changingpw_user.username))
    return render_template('change_pw.html',form=form,user=current_user)

#以下用于收藏博客
@app.route('/collectpost/<post_id>_<user_id>')
@login_required
def collectpost(post_id,user_id):
    new_collect = Collected(user_id=user_id,post_id=post_id)
    db.session.add(new_collect)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id,user_id=user_id))

#以下用于取消收藏
@app.route('/discollectpost/<post_id>_<user_id>')
@login_required
def discollectpost(post_id,user_id):
    discollecting_id = Collected.query.filter(and_(post_id==post_id,user_id==user_id)).first_or_404().id
    discollecting = Collected.query.get(discollecting_id)
    db.session.delete(discollecting)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id,user_id=user_id))

#以下是控制中心方法
@app.route('/acc', methods=['GET', 'POST'])
@login_required
def acc():
    show_comments = False
    sel_comments = None
    sel_postid = 0
    form = AccForm()
    if form.validate_on_submit():
        if form.sel.data == 1:
            if not form.target.data.isdigit():
                flash('id必须是整数')
                return redirect(url_for('acc'))
            sel_postid = int(form.target.data)
            if Post.query.filter_by(id=sel_postid).count() == 0:
                flash('找不到目标')
                return redirect(url_for('acc'))
            return redirect(url_for('editpost',post_id=sel_postid))
        elif form.sel.data == 2:
            if not form.target.data.isdigit():
                flash('id必须是整数')
                return redirect(url_for('acc'))
            sel_postid = int(form.target.data)
            if Post.query.filter_by(id=sel_postid).count() == 0:
                flash('找不到目标')
                return redirect(url_for('acc'))
            return redirect(url_for('deletepost',post_id=sel_postid))
        elif form.sel.data == 3:
            if not form.target.data.isdigit():
                flash('id必须是整数')
                return redirect(url_for('acc'))
            sel_userid = int(form.target.data)
            if User.query.filter_by(id=sel_userid).count() == 0:
                flash('找不到目标')
                return redirect(url_for('acc'))
            return redirect(url_for('acc_edit_user',user_id=sel_userid))
        elif form.sel.data == 4:
            sel_username = form.target.data
            if User.query.filter_by(username=sel_username).count() == 0:
                flash('找不到目标')
                return redirect(url_for('acc'))
            sel_userid = User.query.filter_by(username=sel_username).first().id
            return redirect(url_for('acc_edit_user',user_id=sel_userid))
        else:
            if not form.target.data.isdigit():
                flash('id必须是整数')
                return redirect(url_for('acc'))
            sel_postid = int(form.target.data)
            if Post.query.filter_by(id=sel_postid).count() == 0:
                flash('找不到目标')
                return redirect(url_for('acc'))
            sel_comments = Comment.query.filter_by(post_id=sel_postid).order_by(Comment.timestamp.desc()).all()
            show_comments = True
    return render_template('admin_center.html', user=current_user, form=form, show_comments=show_comments, sel_comments=sel_comments,sel_postid=sel_postid)