from datetime import datetime, timedelta, date
from django.shortcuts import render
from semantic.models import ArticleInfo
from django.core.paginator import Paginator


# Create your views here.

# article.html：得到各类各页的数据
def all_rank(request):
    limit = 10
    page = request.GET.get('page', 1)
    cate = request.GET.get('cate', 'all')
    if cate == 'qiche':
        cate_text = '汽车'
    elif cate == 'difang':
        cate_text = '地方'
    elif cate == 'shishi':
        cate_text = '时事资讯'
    elif cate == 'shuma':
        cate_text = '数码科技'
    elif cate == 'zhichang':
        cate_text = '职场招聘'
    elif cate == 'lvxing':
        cate_text = '旅行'
    else:
        cate_text = '总榜'
    article = ArticleInfo.objects(category=cate_text)
    paginator = Paginator(article, limit)
    load = paginator.page(page)
    context = {
        'article': load,
        'counts': article.count()
    }
    return render(request, 'article.html', context)


# highcharts.html
# 第一、二个图，得到一段时间内公众号阅读量或点赞数超过某个限值的文章总数
def get_and_gen_charts_data(date1, date2, num, limit, cate):
    pipeline = [
        {'$match': {'$and': [{'post_date': {'$gte': datetime.strptime(date1, '%Y-%m-%d'),
                                            '$lte': datetime.strptime(date2, '%Y-%m-%d')}},
                             {cate: {'$gte': num}}]}},
        {'$group': {'_id': '$account', 'total': {'$sum': 1}}},
        {'$sort': {'total': -1}},
        {'$limit': limit}
    ]
    for a in ArticleInfo._get_collection().aggregate(pipeline):
        data = {
            'name': a.get('_id'),
            'y': a.get('total'),
            # 'type': types
        }
        yield data


series_page_views = [data for data in
                     get_and_gen_charts_data('2018-03-12', '2018-03-15', 5000, 20, 'page_views')]
series_like_nums = [data for data in
                    get_and_gen_charts_data('2018-03-12', '2018-03-15', 3000, 20, 'like_nums')]


# print(series_like_nums)


# 第三个图，得到公众号发文总数
def article_nums_charts(limit):
    pipeline = [
        {'$group': {'_id': '$account', 'total': {'$sum': 1}}},
        {'$sort': {'total': -1}},
        {'$limit': limit}
    ]
    for a in ArticleInfo._get_collection().aggregate(pipeline):
        data = [a['_id'], a['total']]
        yield data


data_ary = [data for data in article_nums_charts(15)]
first_data = {
    'name': data_ary[0][0],
    'y': data_ary[0][1],
    'sliced': 'true',
    'selected': 'true'
}
del data_ary[0]
data_ary.insert(0, first_data)
after_data = data_ary


# print(after_data)


# 第四个图，得到一段时间内公众号文章阅读量或点赞数的折线图
# 1：
# 打印一段时间的每一天 如给出2017-12-25,2018-01-05
def get2_all_dates(date1, date2):
    begin_date = date(int(date1.split('-')[0]), int(date1.split('-')[1]), int(date1.split('-')[2]))
    end_date = date(int(date2.split('-')[0]), int(date2.split('-')[1]), int(date2.split('-')[2]))
    days = timedelta(days=1)

    while begin_date <= end_date:
        yield (begin_date.strftime('%Y-%m-%d'))
        begin_date = begin_date + days


date_str_array = []
for da in get2_all_dates('2018-3-13', '2018-3-14'):
    date_str = '{}-{}-{}'.format(da.split('-')[0], da.split('-')[1], da.split('-')[2])
    date_str_array.append(date_str)
print(date_str_array)
account_array = ['人民日报', '央视新闻', '新华社', 'FM93交通之声', '十点读书', '有书', '占豪', '广州日报']


# 2: 生成折线图的数据
def line_chart_data(type):
    for a1 in account_array:
        account_post_nums = []
        for d1 in date_str_array:
            pipeline = [
                {'$match': {'$and': [{'account': a1}, {'post_date': datetime.strptime(d1, '%Y-%m-%d')}]}},
                {'$sort': {'post_date': 1}},
                # {'$limit': 1}
            ]
            for a in ArticleInfo._get_collection().aggregate(pipeline):
                # print(a['account'], a['title'], a['post_date'], a['page_views'], a['like_nums'])
                account_post_nums.append(a[type])
        data = {
            'name': a['account'],
            'data': account_post_nums
        }
        yield data


series_line_chart_page = [data for data in line_chart_data('page_views')]
series_line_chart_like = [data for data in line_chart_data('like_nums')]
print(series_line_chart_page)


# 这是charts页面的调用数据的函数
def highcharts(request):
    context = {
        'chart_page_views': series_page_views,
        'chart_like_nums': series_like_nums,
        'article_nums': after_data,
        'line_chart_page': series_line_chart_page,
        'line_chart_like': series_line_chart_like
    }
    return render(request, 'highcharts.html', context)
