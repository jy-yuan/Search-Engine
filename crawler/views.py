from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from . import models
from .models import News, Entry, ContentEntry
import jieba
import re
import time


def crawl(request):
    browser = webdriver.Chrome('/Users/yjy/Desktop/python/chromedriver')
    browser2 = webdriver.Chrome('/Users/yjy/Desktop/python/chromedriver')
    URL = 'http://www.xinhuanet.com/legal/index.htm'
    browser.get(URL)
    nextbutton = browser.find_element_by_id('dataMoreBtn')
    for i in range(0, 100):
        time.sleep(0.5)
        nextbutton.click()
    el = browser.find_elements_by_xpath(
        '//*[@id="showData0"]/*[@class="clearfix"]')
    for i in el:
        tit = i.find_element_by_xpath('./h3').text
        print (tit)
        tim = i.find_element_by_xpath('./div/span').text
        # print(tim)

        summ = i.find_element_by_xpath('./p').text
        #print (summ)

        el2 = i.find_element_by_xpath('./h3/a')
        site = str(el2.get_attribute('href'))

        browser2.get(site)

        try:
            body = browser2.find_elements_by_xpath('//*[@id="p-detail"]/p')
        except Exception as e:
            continue
        else:
            details = ''
            for j in body:
                details = details + '\r\n' + j.text
            #print (details)

            newone = News(title=tit, time=tim, summary=summ, content=details)
            newone.save()
            seglist = jieba.lcut(tit, cut_all=False)
            entrylist = []
            for j in seglist:
                if len(j) < 2:
                    continue
                entrylist.append(j)
            seglist2 = jieba.lcut(details, cut_all=False)
            contententrylist = []
            for k in seglist2:
                if len(k) < 2:
                    continue
                contententrylist.append(k)
            entrylist = list(set(entrylist))
            contententrylist = list(set(contententrylist))
            for a in entrylist:
                newone.entry_set.create(key=a)
            for b in contententrylist:
                newone.contententry_set.create(key=b)
            # models.News.objects.create(title=tit, time=tim, summary=summ, content=details)
    browser.close()
    browser2.close()
    return HttpResponse("okay! ")


def split(request):
    allnews = News.objects.all()
    for i in allnews:
        print (i.id)
        seglist = jieba.lcut(i.title, cut_all=False)
        entrylist = []
        for j in seglist:
            if len(j) < 2:
                continue
            entrylist.append(j)
        seglist2 = jieba.lcut(i.content, cut_all=False)
        contententrylist = []
        for k in seglist2:
            if len(k) < 2:
                continue
            contententrylist.append(k)
        entrylist = list(set(entrylist))
        contententrylist = list(set(contententrylist))
        for a in entrylist:
            i.entry_set.create(key=a)
        for b in contententrylist:
            i.contententry_set.create(key=b)
    return HttpResponse("okay! ")


def delete(request):
    allnews = News.objects.all()[:200]
    for i in allnews:
        allentries = i.contententry_set.all()
        for j in allentries:
            print (j.id)
    return HttpResponse("okay! ")
# Create your views here.
