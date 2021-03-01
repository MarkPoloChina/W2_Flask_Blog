from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField,FileField,SelectField
from wtforms.validators import DataRequired,Length
from wtforms.validators import ValidationError,Email,EqualTo
from app.models import User
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    #DataRequired，当你在当前表格没有输入而直接到下一个表格时会提示你输入
    username = StringField('用户名',validators=[DataRequired(message='请输入用户名')])
    password = PasswordField('密码',validators=[DataRequired(message='请输入密码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '重复密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')
    #校验用户名是否重复
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已存在')
    #校验邮箱是否重复
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已被注册')

class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名!')])
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    Profile_Pic = FileField('上传头像', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('提交')

class PostForm(FlaskForm):
    title = StringField('标题',validators=[DataRequired(message='请输入标题'), Length(min=0, max=20)])
    body = PageDownField("内容(支持MarkDown)", validators=[DataRequired(message='请输入正文'), Length(min=0, max=140)])
    video = FileField('上传视频', validators=[FileAllowed(['mp4','avi'])])
    cover = FileField('上传封面', validators=[DataRequired(message='请上传封面'),FileAllowed(['jpg','png'])])
    tag = StringField('标签', validators=[Length(min=0, max=10)])
    submit = SubmitField("提交")

class EditPostForm(FlaskForm):
    title = StringField('标题',validators=[DataRequired(message='请输入标题'), Length(min=0, max=20)])
    body = PageDownField("内容(支持MarkDown)", validators=[DataRequired(message='请输入正文'), Length(min=0, max=140)])
    video = FileField('更新视频', validators=[FileAllowed(['mp4','avi'])])
    tag = StringField('标签', validators=[Length(min=0, max=10)])
    cover = FileField('更新封面', validators=[FileAllowed(['jpg','png'])])
    delete_video_or_not = BooleanField('删除视频')
    submit = SubmitField("提交")

class CommentForm(FlaskForm):
    body = StringField('发表评论', validators=[DataRequired(message='请输入评论!')])
    submit = SubmitField("提交")

class ChangePwForm(FlaskForm):
    ori_pw = PasswordField('旧密码',validators=[DataRequired(message='请输入旧密码')])
    new_pw = PasswordField('新密码',validators=[DataRequired(message='请输入新密码')])
    re_pw = PasswordField('重复密码', validators=[DataRequired(message='请输入重复密码'), EqualTo('new_pw')])
    submit = SubmitField('确认')

class MdForm(FlaskForm):
    body = PageDownField('内容')

#以下仅用于ACC
class AccForm(FlaskForm):
    target = StringField('执行目标',validators=[DataRequired(message='请输入目标')])
    sel = SelectField('识别为', validators=[DataRequired('请选择对象类型')], choices=[(1,'博客id-修改'),(2,'博客id-删除'),(3,'用户id-修改'),(4,'用户名-修改'),(5,'博客id-评论')],default = 1,coerce=int)
    submit = SubmitField('执行')