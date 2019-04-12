from django.shortcuts import render
from django.http import HttpResponse
from .import models

import sys
sys.path.append(r'C:\Users\15951\Desktop\外包服务\waibao\smart')
#import FAQ
import os
import time
import logging
from collections import deque
import jieba
import jieba.posseg as pseg
from utils import (
    get_logger,
    similarity,
)


jieba.dt.tmp_dir = "./"
jieba.default_logger.setLevel(logging.ERROR)
logger = get_logger('faqrobot', logfile="faqrobot.log")

class zhishiku(object):
    def __init__(self, q):  # a是答案（必须是1给）, q是问题（1个或多个）
        self.q = [q]
        self.a = ""
        self.sim = 0
        self.q_vec = []
        self.q_word = []

    def __str__(self):
        return 'q=' + str(self.q) + '\na=' + str(self.a) + '\nq_word=' + str(self.q_word) + '\nq_vec=' + str(self.q_vec)
        # return 'a=' + str(self.a) + '\nq=' + str(self.q)


class FAQrobot(object):
    def __init__(self, zhishitxt='FAQ.txt', lastTxtLen=10, usedVec=False):
        # usedVec 如果是True 在初始化时会解析词向量，加快计算句子相似度的速度
        self.lastTxt = deque([], lastTxtLen)
        self.zhishitxt = zhishitxt
        self.usedVec = usedVec
        self.reload()

    def load_qa(self):
        print('问答知识库开始载入')
        self.zhishiku = []
        with open(self.zhishitxt, encoding='utf-8') as f:
            txt = f.readlines()
            abovetxt = 0    # 上一行的种类： 0空白/注释  1答案   2问题
            for t in txt:   # 读取FAQ文本文件
                t = t.strip()
                if not t or t.startswith('#'):
                    abovetxt = 0
                elif abovetxt != 2:
                    if t.startswith('【问题】'): # 输入第一个问题
                        self.zhishiku.append(zhishiku(t[4:]))
                        abovetxt = 2
                    else:       # 输入答案文本（非第一行的）
                        self.zhishiku[-1].a += '\n' + t
                        abovetxt = 1
                else:
                    if t.startswith('【问题】'): # 输入问题（非第一行的）
                        self.zhishiku[-1].q.append(t[4:])
                        abovetxt = 2
                    else:       # 输入答案文本
                        self.zhishiku[-1].a += t
                        abovetxt = 1

        for t in self.zhishiku:
            for question in t.q:
                t.q_word.append(set(jieba.cut(question)))

    def load_embedding(self):
        from gensim.models import Word2Vec
        if not os.path.exists('Word60.model'):
            self.vecModel = None
            return

        # 载入60维的词向量(Word60.model，Word60.model.syn0.npy，Word60.model.syn1neg.npy）
        self.vecModel = Word2Vec.load('Word60.model')
        for t in self.zhishiku:
            t.q_vec = []
            for question in t.q_word:
                t.q_vec.append({t for t in question if t in self.vecModel.index2word})

    def reload(self):
        self.load_qa()
        self.load_embedding()

        print('问答知识库载入完毕')

    def maxSimTxt(self, intxt, simCondision=0.1, simType='simple'):
        """
        找出知识库里的和输入句子相似度最高的句子
        simType=simple, simple_POS, vec
        """
        self.lastTxt.append(intxt)
        if simType not in ('simple', 'simple_pos', 'vec'):
            return 'error:  maxSimTxt的simType类型不存在: {}'.format(simType)

        # 如果没有加载词向量，那么降级成 simple_pos 方法
        embedding = self.vecModel
        if simType == 'vec' and not embedding:
            simType = 'simple_pos'

        for t in self.zhishiku:
            questions = t.q_vec if simType == 'vec' else t.q_word
            in_vec = jieba.lcut(intxt) if simType == 'simple' else pseg.lcut(intxt)

            t.sim = max(
                similarity(in_vec, question, method=simType, embedding=embedding)
                for question in questions
            )
        maxSim = max(self.zhishiku, key=lambda x: x.sim)
        logger.info('maxSim=' + format(maxSim.sim, '.0%'))

        if maxSim.sim < simCondision:
            return '抱歉，我没有理解您的意思。请您询问有关金融证券' \
                   '的话题。'

        return maxSim.a

    def answer(self, intxt, simType='simple'):
        """simType=simple, simple_POS, vec, all"""
        if not intxt:
            return ''

        if simType == 'all':  # 用于测试不同类型方法的准确度，返回空文本
            for method in ('simple', 'simple_pos', 'vec'):
                outtext = 'method:\t' + self.maxSim(intxt, simType=method)
                print(outtext)

            return ''
        else:
            outtxt = self.maxSimTxt(intxt, simType=simType)
            # 输出回复内容，并计入日志
        return outtxt




def show1(request):
    a=FAQrobot(r'C:\Users\15951\Desktop\外包服务\waibao\smart\FAQ.txt',10,False)
    #a=FAQrobot('C:\Users\15951\Desktop\外包服务\waibao\smart\FAQ.txt', 10, False)
    b=request.POST['title']
    c=a.answer(b, 'simple_pos')
    return render(request,'smart/show1.html',{'c':c})




def show(request):
    return render(request,'smart/show.html')


# Create your views here.
def index(request):
    user = models.User.objects.get(id=request.session.get('user_id'))
    return render(request,'smart/index.html',{'user':user})

def sign(request):
    return render(request, 'smart/sign.html')

def create(request):
    account=request.POST.get('account',None)
    password=request.POST.get('password',None)
    if account and password:
        same=models.User.objects.filter(account=account)
        if same:
            message = "用户名已存在，请重新注册！"
            return render(request,'smart/sign.html',{'message':message})
        else:
            models.User.objects.create(account=account, password=password)
            users = models.User.objects.all()
            return render(request, 'smart/login.html', {'users': users})
    else:
        message = "用户名和密码不能为空！"
        return render(request, 'smart/sign.html',{'message':message})

def login(request):
    return render(request,'smart/login.html')

def confirm(request):
    try:
        user = models.User.objects.get(account=request.POST['account'])
        if user.password == request.POST['password'] and user.account==request.POST['account']:
            books = models.Book.objects.order_by('id')
            request.session['user_id'] = user.id
            return render(request, 'smart/home.html',{'user': user, 'books':books})
        else:
            message = "密码不正确，请重新输入！"
            return render(request, 'smart/login.html', {'message': message})
    except:
        message = "用户名不存在，请重新输入！"
        return render(request, 'smart/login.html', {'message': message})

def modify(request):
    user = models.User.objects.get(id=request.session.get('user_id'))
    return render(request, 'smart/modify.html',{'user':user})

def reset(request):
    user=models.User.objects.get(id=request.session.get('user_id'))
    password=request.POST.get('password','null')
    user.password=password
    user.save()
    books = models.Book.objects.order_by('id')
    return render(request,'smart/home.html',{'user':user, 'books':books})

def logout(request):
    del request.session['user_id']
    return render(request, 'smart/login.html')

def home(request):
    user = models.User.objects.get(id=request.session.get('user_id'))
    books = models.Book.objects.order_by('id')
    return render(request,'smart/home.html',{'books':books,'user':user})


def detail(request, book_id):
    book=models.Book.objects.get(pk=book_id)
    return render(request,'smart/detail.html',{'book':book})

def detail_smart(request):  #详情页的传参，功能一，实现用户提问回答的智能化，在dialogue页中显示
    user = models.User.objects.get(id=request.session.get('user_id'))
    question='投资逆回购安全吗'
    #total=models.Total.objects.get(id=207)
    #question=total.content
    #此部分为算法实现，通过用户问题找到标准问
    #title='A股开户是否收费？'
    a=FAQrobot(r'C:\Users\15951\Desktop\外包服务\waibao\smart\FAB.txt',10,False)
    #b=request.POST['title']
    content=a.answer(question, 'simple_pos')
    total=models.Total.objects.get(content=content)
    totals=models.Total.objects.all()[:3]#相关问题
    title=total.title
    #content=total.content
    models.Record.objects.create(question=question, title=title, content=content, user=user)#加入值到历史记录

    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    #功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count=count.count+1
        count.save()
    except:
        models.Count.objects.create(title=title,count=1)

    counts = models.Count.objects.all().order_by('-count')[:4]
    #records = models.Record.objects.filter(user_id=user.id)
    record = models.Record.objects.get(pk=1)
    talk = models.Talk.objects.get(question=question)
    #这里要实现把历史纪录通过算法变成分词，然后写入分词表
    #当历史记录变成分词时，通过将它们create进分词表（带有记录id）
    #从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    #下面是实例
    models.Person.objects.all().delete()
    suggests=['*st股票在什么情况下退市？','如何开户？','A股开户是否收费？','60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest,record=record)
    persons=models.Person.objects.all()




    #功能三关键词的实现
    #parts=models.Part.objects.all()取出全部分词
    #通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    #下面是实例
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', '信用账户','B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords=models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'total': total, 'record':record,'user': user, 'talk': talk, 'counts':counts,'totals':totals,'buzzwords':buzzwords, 'persons':persons})


def dialogue(request):
    user = models.User.objects.get(id=request.session.get('user_id'))
    return render(request,'smart/dialogue.html',{'user':user})

def home_smart(request):    #功能一，实现提问回答的智能化，在home页中提问
    user = models.User.objects.get(id=request.session.get('user_id'))
    question=request.POST['title']
    #此部分为算法实现，通过用户问题找到标准问
    #title='A股开户是否收费？'
    a=FAQrobot(r'C:\Users\15951\Desktop\外包服务\waibao\smart\FAB.txt',10,False)
    #b=request.POST['title']
    content=a.answer(question, 'simple_pos')
    total=models.Total.objects.get(content=content)
    totals=models.Total.objects.all()[:3]#相关问题
    title=total.title
    #content=total.content
    models.Record.objects.create(question=question, title=title, content=content,user=user)
    #records = models.Record.objects.filter(user_id=user.id)
    record=models.Record.objects.get(pk=1)
    # 这里要实现把历史纪录通过算法变成分词，然后写入分词表
    # 当历史记录变成分词时，通过数组将它们create进分词表（带有记录id）
    # 从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    # 下面是实例
    models.Person.objects.all().delete()
    suggests = ['*st股票在什么情况下退市？', '如何开户？', 'A股开户是否收费？', '60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest, record=record)
    persons = models.Person.objects.all()

    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    # 功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count=count.count+1
        count.save()
    except:
        models.Count.objects.create(title=title,count=1)
    counts=models.Count.objects.all().order_by('-count')[:4]
    talk = models.Talk.objects.get(question=question)
    #功能三关键词的实现
    #parts=models.Part.objects.all()取出全部分词
    #通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', '信用账户', 'B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords=models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'persons':persons,'total': total,'user': user, 'talk': talk,'counts':counts,'totals':totals,'buzzwords':buzzwords})




def dialogue_smart(request):  #功能一，实现用户提问回答的智能化，在dialogue页中显示
    user = models.User.objects.get(id=request.session.get('user_id'))
    question=request.POST['title']
    #此部分为算法实现，通过用户问题找到标准问
    #title='A股开户是否收费？'
    a=FAQrobot(r'C:\Users\15951\Desktop\外包服务\waibao\smart\FAB.txt',10,False)
    #b=request.POST['title']
    content=a.answer(question, 'simple_pos')
    total=models.Total.objects.get(content=content)
    totals=models.Total.objects.all()[:3]#相关问题
    title=total.title
    #content=total.content
    models.Record.objects.create(question=question, title=title, content=content, user=user)#加入值到历史记录

    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    #功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count=count.count+1
        count.save()
    except:
        models.Count.objects.create(title=title,count=1)

    counts = models.Count.objects.all().order_by('-count')[:4]
    #records = models.Record.objects.filter(user_id=user.id)
    record = models.Record.objects.get(pk=1)
    talk = models.Talk.objects.get(question=question)
    #这里要实现把历史纪录通过算法变成分词，然后写入分词表
    #当历史记录变成分词时，通过将它们create进分词表（带有记录id）
    #从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    #下面是实例
    models.Person.objects.all().delete()
    suggests=['*st股票在什么情况下退市？','如何开户？','A股开户是否收费？','60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest,record=record)
    persons=models.Person.objects.all()




    #功能三关键词的实现
    #parts=models.Part.objects.all()取出全部分词
    #通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    #下面是实例
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', '信用账户','B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords=models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'total': total, 'record':record,'user': user, 'talk': talk, 'counts':counts,'totals':totals,'buzzwords':buzzwords, 'persons':persons})

def hot(request,count_id): #热门问题的回答
    user = models.User.objects.get(id=request.session.get('user_id'))
    count= models.Count.objects.get(pk=count_id)
    question = count.title

    title=count.title
    total = models.Total.objects.get(title=title)
    totals = models.Total.objects.all()[:3]  # 相关问题
    content = total.content
    models.Record.objects.create(question=question, title=title, content=content, user=user)  # 加入值到历史记录
    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    talk = models.Talk.objects.get(question=question)
    # 功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count = count.count + 1
        count.save()
    except:
        models.Count.objects.create(title=title, count=1)
    counts = models.Count.objects.all().order_by('-count')[:4]
    records = models.Record.objects.filter(user_id=user.id)
    record = models.Record.objects.get(pk=1)
    # 这里要实现把历史纪录通过算法变成分词，然后写入分词表
    # 当历史记录变成分词时，通过数组将它们create进分词表（带有记录id）
    # 从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    # 下面是实例
    models.Person.objects.all().delete()
    suggests = ['*st股票在什么情况下退市？', '如何开户？', 'A股开户是否收费？', '60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest, record=record)
    persons = models.Person.objects.all()

    # 功能三关键词的实现
    # parts=models.Part.objects.all()取出全部分词
    # 通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    # 下面是实例
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', '信用账户', 'B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords = models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'talk':talk,'total': total, 'user': user, 'records': records, 'counts': counts, 'totals': totals,'buzzwords': buzzwords, 'persons': persons})


def advice(request,person_id): #个人推荐的回答
    user = models.User.objects.get(id=request.session.get('user_id'))
    person= models.Person.objects.get(pk=person_id)
    question = person.title
    title=person.title
    total = models.Total.objects.get(title=title)
    totals = models.Total.objects.all()[:3]  # 相关问题
    content = total.content
    models.Record.objects.create(question=question, title=title, content=content, user=user)  # 加入值到历史记录

    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    # 功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count = count.count + 1
        count.save()
    except:
        models.Count.objects.create(title=title, count=1)
    counts = models.Count.objects.all().order_by('-count')[:4]
    records = models.Record.objects.filter(user_id=user.id)
    record = models.Record.objects.get(pk=1)
    talk = models.Talk.objects.get(question=question)
    # 这里要实现把历史纪录通过算法变成分词，然后写入分词表
    # 当历史记录变成分词时，通过数组将它们create进分词表（带有记录id）
    # 从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    # 下面是实例
    models.Person.objects.all().delete()
    suggests = ['*st股票在什么情况下退市？', '如何开户？', 'A股开户是否收费？', '60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest, record=record)
    persons = models.Person.objects.all()

    # 功能三关键词的实现
    # parts=models.Part.objects.all()取出全部分词
    # 通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    # 下面是实例
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', '信用账户', 'B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords = models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'talk':talk, 'total': total, 'user': user, 'records': records, 'counts': counts, 'totals': totals,'buzzwords': buzzwords, 'persons': persons})


def link(request,total_id): #相关问题链接的回答
    user = models.User.objects.get(id=request.session.get('user_id'))
    total= models.Total.objects.get(pk=total_id)
    question = total.title
    title=total.title
    total = models.Total.objects.get(title=title)
    totals = models.Total.objects.all()[:3]  # 相关问题
    content = total.content
    models.Record.objects.create(question=question, title=title, content=content, user=user)  # 加入值到历史记录
    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    talk = models.Talk.objects.get(question=question)
    # 功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count = count.count + 1
        count.save()
    except:
        models.Count.objects.create(title=title, count=1)
    counts = models.Count.objects.all().order_by('-count')[:4]
    records = models.Record.objects.filter(user_id=user.id)
    record = models.Record.objects.get(pk=1)
    # 这里要实现把历史纪录通过算法变成分词，然后写入分词表
    # 当历史记录变成分词时，通过数组将它们create进分词表（带有记录id）
    # 从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    # 下面是实例
    models.Person.objects.all().delete()
    suggests = ['*st股票在什么情况下退市？', '如何开户？', 'A股开户是否收费？', '60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest, record=record)
    persons = models.Person.objects.all()

    # 功能三关键词的实现
    # parts=models.Part.objects.all()取出全部分词
    # 通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    # 下面是实例
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', '信用账户', 'B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords = models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'talk':talk, 'total': total, 'user': user, 'records': records, 'counts': counts, 'totals': totals,'buzzwords': buzzwords, 'persons': persons})


def hot_word(request,buzzword_id): #相关问题链接的回答
    user = models.User.objects.get(id=request.session.get('user_id'))
    buzzword = models.Buzzword.objects.get(pk=buzzword_id)
    a=buzzword.id
    a='10'
    #算法将关键词转换成total
    total= models.Total.objects.get(pk=a)#先随便定义一个total
    question = total.title
    title=total.title
    total = models.Total.objects.get(title=title)
    totals = models.Total.objects.all()[:3]  # 相关问题
    content = total.content
    models.Record.objects.create(question=question, title=title, content=content, user=user)  # 加入值到历史记录
    try:
        talk=models.Talk.objects.get(question=question)
        talk.save()
    except:
        models.Talk.objects.create(question=question,content=content)
    talk = models.Talk.objects.get(question=question)
    # 功能二，实现热门问题，不需要算法
    try:
        count = models.Count.objects.get(title=title)
        count.count = count.count + 1
        count.save()
    except:
        models.Count.objects.create(title=title, count=1)
    counts = models.Count.objects.all().order_by('-count')[:4]
    records = models.Record.objects.filter(user_id=user.id)
    record = models.Record.objects.get(pk=1)
    # 这里要实现把历史纪录通过算法变成分词，然后写入分词表
    # 当历史记录变成分词时，通过数组将它们create进分词表（带有记录id）
    # 从分词表中取出属于该用户的分词进行分析，然后得出四条标准问，用数组返回
    # 下面是实例
    models.Person.objects.all().delete()
    suggests = ['*st股票在什么情况下退市？', '如何开户？', 'A股开户是否收费？', '60岁以上如何开立信用账户？']
    for suggest in suggests:
        models.Person.objects.create(title=suggest, record=record)
    persons = models.Person.objects.all()

    # 功能三关键词的实现
    # parts=models.Part.objects.all()取出全部分词
    # 通过算法将提取出四个关键词,取出关键词之后将其存入关键词表中。
    # 下面是实例
    models.Buzzword.objects.all().delete()
    words = ['逆回购', '开户', 'A股账户', 'B股账户']
    for word in words:
        models.Buzzword.objects.create(word=word)
    buzzwords = models.Buzzword.objects.all()
    return render(request, 'smart/dialogue.html', {'talk':talk,'total': total, 'user': user, 'records': records, 'counts': counts, 'totals': totals,'buzzwords': buzzwords, 'persons': persons})


def home_dialogue(request):
    try:
        user = models.User.objects.get(id=request.session.get('user_id'))
        book = models.Book.objects.get(title=request.POST['title'])
        title=book.title
        content=book.content
        models.Word.objects.create(title=title, content=content,link=user)
        words=models.Word.objects.filter(link_id=user.id)
        return render(request,'smart/dialogue.html',{'book':book,'user':user,'words':words})
    except:
        return render(request,'smart/home.html')


def dialogue_action(request):
    try:
        user = models.User.objects.get(id=request.session.get('user_id'))
        book = models.Book.objects.get(title=request.POST['title'])
        title=book.title
        content=book.content
        models.Word.objects.create(title=title, content=content,link=user)
        words=models.Word.objects.filter(link_id=user.id)
        return render(request,'smart/dialogue.html',{'book':book,'user':user,'words':words})
    except:
        return render(request,'smart/dialogue.html')

def feed(request):
    return render(request,'smart/feed.html')








