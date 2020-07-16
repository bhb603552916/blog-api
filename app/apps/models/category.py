import datetime

from bson import ObjectId
from flask import current_app
from mongoengine import *
from apps import db
from apps.core.error import NotFound
from apps.utils import paginate


class Category(db.DynamicDocument):
    category_name = StringField()
    thumbnail = StringField()
    pub_time = DateTimeField()
    update_time = DateTimeField()

    meta = {
        'allow_inheritance': True,
        'indexes': ['category_name'],
        'ordering': ['-pub_time']
    }

    def to_dict(self):
        cat_dict = {}
        cat_dict['id'] = str(self.id)
        cat_dict['category_name'] = self.category_name
        cat_dict['thumbnail'] = self.thumbnail
        cat_dict['create_time'] = self.pub_time
        return cat_dict

    def save(self, *args, **kwargs):
        now = datetime.datetime.now()
        if not self.pub_time:
            self.pub_time = now
        self.update_time = now
        return super(Category, self).save(*args, **kwargs)

    @property
    def _thumbnail(self):
        site_domain = current_app.config.get('SITE_DOMAIN') if current_app.config.get(
            'SITE_DOMAIN') else "http://127.0.0.1:5000"
        if self.thumbnail is not None:
            return site_domain + self.thumbnail

    @classmethod
    def create_cat(cls, form):
        category = Category(category_name=form.category_name.data, thumbnail=form.thumbnail.data)
        category.save()
        return True

    @classmethod
    def get_cats(cls, cat_name):
        start, count = paginate()  # 获取分页配置
        if cat_name:
            categories = Category.objects.filter(category_name__icontains=cat_name)  # 查询字段包含cat_name的对象
        else:
            categories = Category.objects.skip(start).limit(count).all()  # .exclude('author')  排除某些字段
        if not categories:
            raise NotFound(msg='没有找到分类')
        cats = [cat.to_dict() for cat in categories]
        total = categories.count()
        return cats, total

    @classmethod
    def get_detail(cls, cid):
        cat = Category.objects(id=ObjectId(cid)).first()
        if cat is None:
            raise NotFound(msg='没有找到相关分类')
        return cat.to_dict()

    @classmethod
    def remove_cat(cls, cid):
        cat = Category.objects(id=ObjectId(cid)).first()
        if cat is None:
            raise NotFound(msg='没有找到相关分类')
        cat.delete()
        return True

    @classmethod
    def edit_cat(cls, cid, form):
        cat = Category.objects(id=ObjectId(cid)).first()
        if cat is None:
            raise NotFound(msg='没有找到相关分类')
        cat.update(category_name=form.category_name.data, thumbnail=form.thumbnail.data)
        return True

    @classmethod
    def get_correct(cls, tid):
        """
        所属文章数量
        :param tid:
        :return:
        """
        pass