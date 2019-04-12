from django.db import models

# Create your models here.
class User(models.Model):
    account=models.CharField(max_length=20,null=False)
    password=models.CharField(max_length=20,null=False)

class Repository(models.Model):#无用数据表
    title=models.CharField(max_length=64, null=False)
    content=models.TextField(null=False)

class Information(models.Model):#无用数据表
    title=models.CharField(max_length=64, null=False)
    content=models.TextField(null=False)

class Book(models.Model):#无用数据表
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)

class Search(models.Model):#无用数据表
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)
    link = models.ForeignKey('User',on_delete=models.CASCADE)

class Word(models.Model):
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)
    link = models.ForeignKey('User',on_delete=models.CASCADE)

class Record(models.Model):
    title = models.CharField(max_length=64, null=False)
    question = models.CharField(max_length=64, null=False)
    content = models.TextField(null=True)
    user = models.ForeignKey('User',on_delete=models.CASCADE)

class Part(models.Model):   #分词
    word = models.CharField(max_length=64, null=False)
    record = models.ForeignKey('Record', on_delete=models.CASCADE)

class Person(models.Model):   #个人推荐
    title = models.CharField(max_length=64, null=False)
    record = models.ForeignKey('Record', on_delete=models.CASCADE)

class Buzzword(models.Model):  #关键词
    word = models.CharField(max_length=64, null=False)

class Data(models.Model):#无用数据表
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)

class Count(models.Model):   #热门问题
    title = models.CharField(max_length=64, null=False)
    count = models.IntegerField(default=1)

class Tatol(models.Model):#无用数据表
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)

class Total(models.Model):    #数据集
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)

class Talks(models.Model):    #无用数据表
    question = models.CharField(max_length=64, null=False)
    content = models.TextField(null=True)

class Talk(models.Model):    #对话存储内容
    question = models.CharField(max_length=64, null=False)
    content = models.TextField(null=True)