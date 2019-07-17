from django.shortcuts import render
from crawl.models import News, Entry
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from operator import itemgetter, attrgetter
import time
from math import *
import jieba
import re
import operator


def all(request):
    news_list = list(reversed(News.objects.order_by('time')))
    paginator = Paginator(news_list, 20)
    page = request.GET.get('page')
    try:
        news_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        news_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        news_list = paginator.page(paginator.num_pages)
    return render(request, "news/all.html", locals())


def detail(request, news_id):
    news = News.objects.get(id=news_id)
    seglist = jieba.lcut(news.content, cut_all=False)
    wordcount = len(seglist)
    newscount = len(News.objects.all())
    entryset = news.contententry_set.all()
    keys = []
    counts = []
    for i in entryset:
        keys.append(i.key)
    dictionary = {}
    for key in keys:
        count = 0
        for segs in seglist:
            if key == segs:
                count = count + 1
        havethiskeycount = len(Entry.objects.filter(key=key))
        dictionary[key] = log(newscount/(havethiskeycount+1))*count/wordcount
    sorted_dict = sorted(dictionary.items(),
                         key=operator.itemgetter(1), reverse=True)
    key1 = sorted_dict[2][0]
    key2 = sorted_dict[3][0]
    # print(key1)
    # print(key2)
    result = []
    news1 = News.objects.filter(entry__key=key1)
    news2 = News.objects.filter(entry__key=key2)
    news3 = News.objects.filter(
        contententry__key=key1).filter(contententry__key=key2)
    for i in news1:
        if i == news:
            continue
        if len(result) == 3:
            break
        result.append(i)
    for i in news2:
        if i == news:
            continue
        if len(result) == 3:
            break
        result.append(i)
    for i in news3:
        if i == news:
            continue
        if len(result) == 3:
            break
        result.append(i)
    # print(sorted_dict)
    body = news.content.split('\r\n')
    return render(request, "news/detail.html", locals())


def search(request):
    key = request.GET['search']
    fromdate = request.GET['from']
    todate = request.GET['to']
    if len(key) >= 4:
        return searchmore(request, key, fromdate, todate)
    if not fromdate:
        fromdate = '2018-01-01'
    if not todate:
        todate = '2019-01-01'
    #entries = Entry.objects.filter(key=key)
    starttime = time.time()
    newss = News.objects.filter(entry__key=key)
    newsss = News.objects.filter(contententry__key=key)
    endtime = time.time()
    timeelapsed = round(endtime - starttime, 8)
    news_list = []
    for i in newss:
        tmptime = i.time[0:10]
        if tmptime >= fromdate and tmptime <= todate:
            news_list.append(i)
    for j in newsss:
        tmptime = j.time[0:10]
        if tmptime >= fromdate and tmptime <= todate:
            news_list.append(j)
    #news_list = list(set(news_list))
    for k in news_list:
        k.title = k.title.replace(key, '<em>' + key + '</em>')
        position = k.content.find(key)
        if position < 40:
            a = 0
        else:
            a = position - 40
        if position > len(k.content)-40:
            b = len(k.content)-1
        else:
            b = position+40
        k.summary = '...' + k.content[a:b].replace(key, '<em>' + key + '</em>') + '...'
    size = len(news_list)
    paginator = Paginator(news_list, 20)
    page = request.GET.get('page')
    try:
        news_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        news_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)
    return render(request, "news/search.html", locals())


def searchmore(request, tmpkeys, fromdate, todate):
    keys = jieba.lcut(tmpkeys)
    key = tmpkeys
    if not fromdate:
        fromdate = '2018-01-01'
    if not todate:
        todate = '2019-01-01'
    starttime = time.time()
    news = []
    '''
    for i in keys:
        news += News.objects.filter(entry__key=i)
    for i in keys:
        news += News.objects.filter(contententry__key=i)
        '''
    print (keys)
    tmpnews = News.objects.filter(entry__key=keys[0]).filter(contententry__key=keys[1])
    for i in tmpnews:
        i.title = i.title.replace(keys[0], '<em>' + keys[0] + '</em>')
        i.title = i.title.replace(keys[1], '<em>' + keys[1] + '</em>')
        position = i.content.find(keys[1])
        if position < 40:
            a = 0
        else:
            a = position - 40
        if position > len(i.content) - 40:
            b = len(i.content) - 1
        else:
            b = position + 40
        i.summary = '...'+i.content[a:b].replace(keys[1], '<em>' + keys[1] + '</em>')+'...'
        news.append(i)
    tmpnews2 = News.objects.filter(entry__key=keys[1]).filter(contententry__key=keys[0])
    for i in tmpnews2:
        i.title = i.title.replace(keys[1], '<em>' + keys[1] + '</em>')
        i.title = i.title.replace(keys[0], '<em>' + keys[0] + '</em>')
        position = i.content.find(keys[0])
        if position < 40:
            a = 0
        else:
            a = position - 40
        if position > len(i.content) - 40:
            b = len(i.content) - 1
        else:
            b = position + 40
        i.summary = '...'+i.content[a:b].replace(keys[0], '<em>' + keys[0] + '</em>')+'...'
        news.append(i)
    for i in keys[2:]:
        tmpnews3 = News.objects.filter(contententry__key=i)
        for k in tmpnews3:
            k.title = k.title.replace(i, '<em>' + i + '</em>')
            position = k.content.find(i)
            if position < 40:
                a = 0
            else:
                a = position - 40
            if position > len(k.content) - 40:
                b = len(k.content) - 1
            else:
                b = position + 40
            k.summary = '...'+k.content[a:b].replace(i, '<em>' + i + '</em>')+'...'
        news += tmpnews3
    endtime = time.time()
    timeelapsed = round(endtime - starttime, 8)
    news_list = []
    for i in news:
        tmptime = i.time[0:10]
        if tmptime >= fromdate and tmptime <= todate:
            news_list.append(i)
    # news_list = list(set(news_list))
    size = len(news_list)
    paginator = Paginator(news_list, 20)
    page = request.GET.get('page')
    try:
        news_list = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        news_list = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
    except EmptyPage:
        news_list = paginator.page(paginator.num_pages)
    return render(request, "news/search.html", locals())

# Create your views here.
