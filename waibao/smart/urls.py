from django.contrib import admin
from django.urls import path
from django.urls import path, re_path
from django.conf.urls import url
from .import views as bv
app_name='[smart]'
urlpatterns = [
  path('index/', bv.index,name='index'),
  path('sign/',bv.sign,name='sign'),
  path('create/',bv.create,name='create'),
  path('login/', bv.login,name='login'),
  path('modify/',bv.modify,name='modify'),
  path('confirm/', bv.confirm, name='confirm'),
  path('reset/', bv.reset, name='reset'),
  path('logout/', bv.logout, name='logout'),
  path('home/',bv.home,name='home'),
  re_path('detail/(?P<book_id>[0-9]+)', bv.detail,name='detail'),
  path('dialogue/',bv.dialogue,name='dialogue'),
  path('dialogue_action/',bv.dialogue_action,name='dialogue_action'),
  path('home_dialogue/',bv.home_dialogue,name='home_dialogue'),
  path('feed/',bv.feed,name='feed'),
  re_path('hot/(?P<count_id>[0-9]+)', bv.hot,name='hot'),#热门问题的回答
  re_path('advice/(?P<person_id>[0-9]+)',bv.advice,name='advice'),#个人推荐的回答
  re_path('link/(?P<total_id>[0-9]+)', bv.link, name='link'),  # 相关问题的链接回答
  re_path('hot_word/(?P<buzzword_id>[0-9]+)', bv.hot_word, name='hot_word'),  # 关键词的回答
  path('dialogue_smart/', bv.dialogue_smart,name='dialogue_smart'),
  path('detail_smart/', bv.detail_smart, name='detail_smart'),
  path('home_smart/',bv.home_smart,name='home_smart'),
  path('show/',bv.show,name='show'),
  path('show1/',bv.show1,name='show1'),
]