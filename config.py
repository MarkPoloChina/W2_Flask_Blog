import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #设置密匙要没有规律，别被人轻易猜到哦
    SECRET_KEY = 'a9087FFJFF9nnvc2@#$%FSD'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:26239122xzw@localhost:3306/flaskblog?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False