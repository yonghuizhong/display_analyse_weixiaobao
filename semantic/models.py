from django.db import models
from mongoengine import *
from datetime import datetime
connect('weixiaobao', host='127.0.0.1', port=27017)


# Create your models here.


class ArticleInfo(Document):
    title = StringField()
    contents = StringField()
    account = StringField()
    page_views = IntField()
    like_nums = IntField()
    category = StringField()
    href = StringField()
    page_link = StringField()
    original_tag = IntField()
    spread_nums = StringField()
    post_date = DateTimeField()
    meta = {'collection': 'all_links'}  # 好像要把这个表的所有属性写上


# for i in ArticleInfo.objects[0:4]:
#     # print(i.title, '\n', i.contents)
#     print(i.account, i.page_views, i.post_date)
#     print('\n')

pipeline = [
    {'$match': {'$and': [{'post_date': {'$gte': datetime.strptime('2018年3月12日', '%Y年%m月%d日'),
                                        '$lte': datetime.strptime('2018年3月15日', '%Y年%m月%d日')}},
                         {'page_views': {'$gte': 5000}}]}},
    {'$group': {'_id': '$account', 'total': {'$sum': 1}}},
    {'$sort': {'total': -1}},
    {'$limit': 20}
]
for i in ArticleInfo._get_collection().aggregate(pipeline):
    print(i)
