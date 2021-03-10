# W2_Flask_Blog

## 项目说明

- 用于西二python组三轮考核任务

- 基于Flask框架 Mysql数据库

- 注意！Mysql未整合，不能直接调用

- 包含开源组件 dplayer

- Flask_Blog V1.0 2021.1.26-2021.2.26

- © Mark Polo

## 依赖相关

    pip install flask flask_sqlalchemy flask_migrate flask_login flask_pagedown flask_wtf email_validator pymysql

## 用法&功能

- 创建账号，登录账户，注销账号，登录保持

- 基于dplayer的视频上传显示功能，通过在线弹幕API支持弹幕功能

- 基于WTF的表单功能，同时支持基于PageDown的Md在线预览

- 基于Mysql的数据库，每种数据分别建立映射模型，通过外键相关联

- 根据时间戳对目标博客进行排序

## 开发过程难点

- mysql数据库的模型映射和表间关系十分令人困惑。期间遇到各种拒绝修改的sql报错。比如，对于一个post类表单的主键id，若与不同的两个表单，如Liked和Collected的post_id字段绑定外键时，mysql报多外键错误，这时建立的relationship()将不能定位到一个具体的值。网上有其他做法，比如先设置sql不检查外键，在方法完成时再重现复原；我则放弃了直接用backref访问，而是单独做一个db查询，直接去查询对应表的字段值，然后按要求的顺序排列，通过控制list的index的遍历达到相同的要求。

- 基本上，对于密码储存，普遍的做法是不放明文于数据库，这就要求使用合适的加密方法对密码明文进行处理。我使用了md5方法，首先自然是from hashlib import md5，然后在模型中定义了set和check两个方法，用于接收来自form的明文并转成密文。期间需用的秘钥，通过随机设置放置于config中。check同样加密并将密文与数据库的做比对。

- 路由方面，必须用从url前端传递过来的参数确定一个资源或含参方法，所以路径变量需要合理设置。如，定位到某一评论时，我们需要知道post_id，也要知道comment_id，因为用户从post中定位，故必须含两个参数，用经典的rest路径方法就是/post/<post_id>/<comment_id>。

- 文件io方面，使用的是随机文件名与post表绑定，避免查询混乱。
