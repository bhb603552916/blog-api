# -*- coding:utf-8 -*-
"""
用户模型
"""
from flask import request
from flask import current_app, g
from mongoengine import *
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from apps.core.error import NotFound, ParameterException
# from apps.models.comment import Comment


class User(DynamicDocument):
    username = StringField(max_length=128)
    nickname = StringField(max_length=128, default=None)
    avatar = StringField()
    is_superuser = BooleanField(default=False)
    create_time = DateTimeField()
    ip = StringField()
    permissions = ListField()
    # comment = ReferenceField(Comment)
    # avatar_hash = StringField()
    update_time = DateTimeField()
    role = IntField(max_length=32, default=0)  # choices=ROLES
    email = EmailField(default=None)
    last_login = DateTimeField(default=datetime.datetime.now, required=True)
    _password = StringField()

    def __str__(self):  # 建议: 给每个模型增加 __str__ 方法，它返回一个具有可读性的字符串表示模型，可在调试和测试时使用
        return self.username + '' + self._password

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()
        if not self.create_time:
            self.create_time = now
        self.update_time = now
        return super(User, self).save(*args, **kwargs)

    def to_dict(self):
        user_dict = self.to_mongo().to_dict()
        user_dict['id'] = user_dict['_id']
        del user_dict['_id']
        del user_dict['_password']
        return user_dict

    @property  # 这个装饰器起到只读的作用
    def set_avatar(self):
        site_domain = current_app.config.get('SITE_DOMAIN') if current_app.config.get(
            'SITE_DOMAIN') else "http://127.0.0.1:5000"
        if self.avatar is not None:
            return site_domain + self.avatar  # os.path.join(current_app.static_url_path, self._avatar)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    @property
    def permission(self):
        return self.permissions

    @permission.setter
    def permission(self, raw):
        self.permissions = generate_password_hash(raw)

    @staticmethod
    def get_current_user(self):
        # 获取当前用户
        return g.user

    @classmethod
    def verify(cls, username, password):
        user = cls.objects(username=username).first()
        # user.id = str(user.id)  # Mongodb是ObjectId，此处转化成str类型，不然会报错
        if user is None:
            raise NotFound(msg='未找到该用户信息')
        if not user.check_password(password):
            raise ParameterException(msg='密码错误，请重新输入')
        return {'uid': str(user.id)}

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    @staticmethod
    def reset_password(uid, new_password):
        # user = User()
        user = User.objects(id=uid).first()
        user.update(set___password=generate_password_hash(new_password))
        return user

    def change_password(self, uid, old_password, new_password):
        if self.check_password(old_password):
            user = User.objects(id=uid).first()
            user.update(set___password=generate_password_hash(new_password))
            return user

    @staticmethod
    def get_ip():
        """
        获取用户的IP
        """
        if request.headers.getlist("X-Forwarded-For"):
            return request.headers.getlist("X-Forwarded-For")[0]
        if 'Cdn-Real-Ip' in request.headers:
            return request.headers['Cdn-Real-Ip']

        return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)


    # pass
