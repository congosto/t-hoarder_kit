#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mariluz Congosto
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

import os
import re
import sys
import time
import datetime
from datetime import timedelta
import unicodedata
import math
import codecs
import argparse

#  
def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

# # A dinamic matrix
# # This matrix is a dict whit only cells it nedeed
# # Column and row numbers start with 1
#  
class AvgDict(dict):
    def __init__(self):
        self._total = 0.0
        self._count = 0

    def __setitem__(self, k, v):
        if k in self:
            self._total -= self[k]
            self._count -= 1
        dict.__setitem__(self, k, v)
        self._total += v
        self._count += 1

    def __delitem__(self, k):
        v = self[k]
        dict.__delitem__(self, k)
        self._total -= v
        self._count -= 1
        
    def store (self,k,v):
        if k not in self:
          self[k]=v
          self._count += 1
        else:
          old_value=self[k]
          self[k]=old_value+v
        self._total += v
        return 
          
    def store_unique (self,k,v):
      if k not in self:
        self[k]=v
        self._count += 1
        self._total = v
        return   
        
    def getitem (self,k):
      if k not in self:
        return 0
      else:
        return self[k]

    def average(self):
        if self._count:
            return self._total/self._count
    
    def total(self):
        total_v =0
        for v in self:
          total_v += v
        return total_v
    
    def reset(self):
        self._total = 0.0
        self._count = 0
        return

class Matrix(dict):
  def __init__(self):
    return

  def setitem(self, row, col, v):
      dict.__setitem__(self,(row,col),v)
      return

  def getitem(self, row,col):
    if (row,col) not in self:
      return 0
    else:
      return self[(row,col)]  

  def store(self, row, col, v):
    if (row,col) not in self:
      dict.__setitem__(self,(row,col),v)
    else:
       old_value=self[(row,col)] 
       dict.__setitem__(self,(row,col),v+old_value)
    return

  def store_unique(self, row, col, v):
    if (row,col) not in self:
      dict.__setitem__(self,(row,col),v)
    return

class Counters(object):
  def __init__(self,  prefix,path_experiment,dict_stopwords,top_size):
     self.prefix=prefix
     self.path_experiment=path_experiment
     self.dict_stopwords=dict_stopwords
     self.top_size = top_size
     self.count_tweets =0
     self.dict_tweets=AvgDict()
     self.top_authors=[]
     self.dict_apps=AvgDict()
     self.top_apps=[]
     self.dict_locs=AvgDict()
     self.top_locs=[]
     self.dict_words=AvgDict()
     self.top_words=[]
     self.dict_hashtags=AvgDict()
     self.top_hashtags=[]
     self.dict_users_reply=AvgDict()
     self.top_users_reply=[]
     self.dict_users_RT=AvgDict()
     self.top_users_RT=[]
     self.dict_users_mention=AvgDict()
     self.top_users_mention=[]
     self.dict_tweets_day=AvgDict()
     self.dict_RT_day=AvgDict()
     self.dict_reply_day=AvgDict()
     self.dict_mention_day=AvgDict()
     self.dict_authors_unique_day=AvgDict()
     self.dict_authors_new_day=AvgDict()
     self.dict_authors_old_day=AvgDict()
     self.tweets_day_order=[]
     self.dict_authors_day=Matrix()
     self.dict_top_authors_day=Matrix()
     self.dict_top_users_RT_day=Matrix()
     self.dict_top_users_reply_day=Matrix()
     self.dict_top_users_mention_day=Matrix()
     self.dict_top_apps_day=Matrix()
     self.dict_top_locs_day=Matrix()
     self.dict_top_words_day=Matrix()
     self.dict_top_hashtags_day=Matrix()
     return

  def reset(self):
     self.count_tweets =0
     self.dict_tweets.clear()
     self.dict_apps.clear()
     self.dict_locs.clear()
     self.dict_words.clear()
     self.dict_hashtags.clear()
     return  

  def reset_day(self):
     self.count_tweets =0
     self.dict_tweets_day.clear()
     self.dict_RT_day.clear()
     self.dict_reply_day.clear()
     self.dict_mention_day.clear()
     self.dict_authors_day.clear()
     self.dict_authors_new_day.clear()
     self.dict_authors_old_day.clear()
     self.dict_top_authors_day.clear()
     self.dict_top_apps_day.clear()
     self.dict_top_locs_day.clear()
     self.dict_top_words_day.clear()
     self.dict_top_hasgtags_day.clear()
     return  

  def token_words (self,source):
    list_words=[]
    source_without_urls=u''
  #renove urls from tweet
    urls=re.findall (r'(http[s]*://\S+)', source,re.U)
    for url in urls:
      start=source.find(url)
      end=len(url)
      source_without_urls=source_without_urls+source[0:start-1]
      source=source[start+end:] 
    source_without_urls=source_without_urls+source
    list_tokens=re.findall (r'[#@]*\w+', source_without_urls,re.U) 
#  remove users and hashtags
    for token in list_tokens:
      if (token.find('#') == -1) and (token.find('@') == -1):
        number= re.search(r'\d+',token)
        if not number:
          token=token.lower()
          list_words.append(token)
    return list_words

  def token_hashtags (self,source):
    source=strip_accents (source)
    list_tokens=re.findall (r'#\w+', source,re.U)
    return list_tokens

  def write_top (self,top,type_top):
    f_file=codecs.open(self.path_experiment+self.prefix+'_'+type_top+'.txt', 'w',encoding='utf-8', errors='ignore')
    for item in top:
      f_file.write('%s\n' %(item))
    f_file.close()

  ####### methods ################

  def set_tweets_day(self,date,text):
    self.count_tweets += 1
    self.dict_tweets_day.store(date,1)
    list_mentions=re.findall (r'@\w+', text)
    if len (list_mentions) >0:
      if re.match(r'[\.]*(@\w+)[^\t\n]+',text):
        self.dict_reply_day.store(date,1)
      elif re.match('[rt[\s]*(@\w+)[:]*',text,re.U):
        self.dict_RT_day.store(date,1)
      self.dict_mention_day.store(date,1)
    return

  def get_tweets_day(self):     
     self.tweets_day_order=sorted([(key,value) for (key,value) in self.dict_tweets_day.items()])
     f_out=  codecs.open(self.path_experiment+self.prefix+'_tweets_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date\tN. Tweets\tN. RTs\tN. Replies\tN. Mentions\n")
     for  (key,value) in self.tweets_day_order:
        f_out.write ('%s\t%s\t%s\t%s\t%s\n' % (key,self.dict_tweets_day.getitem(key),self.dict_RT_day.getitem(key),self.dict_reply_day.getitem(key),self.dict_mention_day.getitem(key)))
     f_out.close()
     return

  def set_author(self, author):
    self.count_tweets += 1
    self.dict_tweets.store(author,1)
    return

  def get_authors(self):
    num_authors=len(self.dict_tweets)
    top_size=self.top_size
    print 'N.Tweets %s\t N. authors %s' % (self.count_tweets,num_authors)
    authors_rank_order=sorted([(value,key) for (key,value) in self.dict_tweets.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_authors.txt', 'w',encoding='utf-8') 
    f_out.write ("Author\tN. Tweets\n")
    for (value,key) in authors_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_authors:
      top_size =num_authors
    for i in range (0,top_size):
      (value,author)=authors_rank_order[i]
      self.top_authors.append(author)
    self.write_top (self.top_authors,'top_authors')
    f_out.close()
    return

  def set_authors_day(self,date,author):
      if (date,author) not in self.dict_authors_day:
        self.dict_authors_unique_day.store(date,1)
        if author in self.dict_tweets:
          self.dict_authors_old_day.store(date,1)
        else:
          self.dict_authors_new_day.store(date,1)
      if author in self.top_authors:
        index= self.top_authors.index(author)
        self.dict_top_authors_day.store(date,index,1)
      self.dict_tweets.store(author,1)
      self.dict_authors_day.store(date,author,1)
      return

  def get_authors_day(self):     
     #write general twittering frecuency 
     f_out=  codecs.open(self.path_experiment+self.prefix+'_authors_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date\tN. Tweets\t N. Unique users\t N. New users\n")
     for  (key,value) in self.tweets_day_order:
        f_out.write ('%s\t%s\t%s\t%s\n' % (key,self.dict_tweets_day.getitem(key),self.dict_authors_unique_day.getitem(key),self.dict_authors_new_day.getitem(key)))
     f_out.close()
     #write top authors frecuency 
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_authors_day.txt', 'w',encoding='utf-8') 
     f_out.write ("date")
     for author in self.top_authors:
       f_out.write ("\t%s" % (author))
     top_size=len(self.top_authors)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write ('\t%s' % (self.dict_top_authors_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return

  def set_user_mention(self,text):
    list_mentions=re.findall (r'@\w\w+', text)
    if len (list_mentions) >0:
      user=list_mentions[0]
      if re.match(r'[\.]*(@\w+)[^\t\n]+',text):
        self.dict_users_reply.store(user,1)
      elif re.match('[rt[\s]*(@\w+)[:]*',text,re.U):
        self.dict_users_RT.store(user,1)
      for user in list_mentions:
        self.dict_users_mention.store(user,1)
    return

  def get_users_reply(self):
    num_users_reply=len(self.dict_users_reply)
    top_size=self.top_size
    users_reply_rank_order=sorted([(value,key) for (key,value) in self.dict_users_reply.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_replies.txt', 'w',encoding='utf-8') 
    f_out.write ("User\tN. Replies\n")
    for (value,key) in users_reply_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_users_reply:
      top_size =num_users_reply
    for i in range (0,top_size):
      (value,user)=users_reply_rank_order[i]
      self.top_users_reply.append(user)
    f_out.close()
    return

  def get_users_RT(self):
    num_users_RT=len(self.dict_users_RT)
    top_size=self.top_size
    users_RT_rank_order=sorted([(value,key) for (key,value) in self.dict_users_RT.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_RT.txt', 'w',encoding='utf-8') 
    f_out.write ("User\tN. RTs\n")
    for (value,key) in users_RT_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_users_RT:
      top_size =num_users_RT
    for i in range (0,top_size):
      (value,user)=users_RT_rank_order[i]
      self.top_users_RT.append(user)
    f_out.close()
    return

  def get_users_mention(self):
    num_users_mention=len(self.dict_users_mention)
    top_size=self.top_size
    users_mention_rank_order=sorted([(value,key) for (key,value) in self.dict_users_mention.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_mentions.txt', 'w',encoding='utf-8') 
    f_out.write ("User\tN. Mentions\n")
    for (value,key) in users_mention_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_users_mention:
      top_size =num_users_mention
    for i in range (0,top_size):
      (value,user)=users_mention_rank_order[i]
      self.top_users_mention.append(user)
    self.write_top (self.top_users_mention,'top_mentions')
    f_out.close()
    return

  def set_user_mention_day(self,date,text):
    list_mentions=re.findall (r'@\w+', text)
    if len (list_mentions) >0:
      user=list_mentions[0]
      if re.match(r'[\.]*(@\w+)[^\t\n]+',text):
        if user in self.top_users_reply:
          index= self.top_users_reply.index(user)
          self.dict_top_users_reply_day.store(date,index,1)
      elif re.match('[rt[\s]*(@\w+)[:]*',text,re.U):
        if user in self.top_users_RT:
          index= self.top_users_RT.index(user)
          self.dict_top_users_RT_day.store(date,index,1)
      for user in list_mentions:
        if user in self.top_users_mention:
          index= self.top_users_mention.index(user)
          self.dict_top_users_mention_day.store(date,index,1)
    return

  def get_users_reply_day(self):     
     #write general twittering frecuency 
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_reply_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date")
     for user in self.top_users_reply:
       f_out.write ("\t%s" % (user))
     top_size=len(self.top_users_reply)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write ('\t%s' % (self.dict_top_users_reply_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return  

  def get_users_RT_day(self):     
     #write general twittering frecuency 
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_RT_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date")
     for user in self.top_users_RT:
       f_out.write ("\t%s" % (user))
     top_size=len(self.top_users_RT)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write (',%s' % (self.dict_top_users_RT_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return 

  def get_users_mention_day(self):     
     #write general twittering frecuency 
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_mention_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date")
     for user in self.top_users_mention:
       f_out.write ("\t%s" % (user))
     top_size=len(self.top_users_mention)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write ('\t%s' % (self.dict_top_users_mention_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return

  def set_app(self, app):
    self.dict_apps.store(app,1)
    return

  def get_apps(self):
    num_apps=len(self.dict_apps)
    top_size=self.top_size
    print 'Num apps %s' % (num_apps)
    apps_rank_order=sorted([(value,key) for (key,value) in self.dict_apps.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_apps.txt', 'w',encoding='utf-8') 
    f_out.write ("App\tN. Tweets\n")
    for (value,key) in apps_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_apps:
      top_size =num_apps
    for i in range (0,top_size):
      (value,app)=apps_rank_order[i]
      self.top_apps.append(app)
    self.write_top (self.top_apps,'top_apps')  
    f_out.close()
    return

  def set_apps_day(self,date,app):
    if app in self.top_apps:
       index= self.top_apps.index(app)
       self.dict_top_apps_day.store(date,index,1)
    return

  def get_apps_day(self):     
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_apps_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date")
     for app in self.top_apps:
       f_out.write ("\t%s" % (app))
     top_size=len(self.top_apps)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write ('\t%s' % (self.dict_top_apps_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return

  def set_loc(self, loc):
      if (loc=='none') or (len(loc)==0):
        self.dict_locs.store('desconocida',1)
      else:
        self.dict_locs.store(loc,1)
      return

  def get_locs(self):
    num_locs=len(self.dict_locs)
    top_size=self.top_size
    print 'Num locs %s' % (num_locs)
    locs_rank_order=sorted([(value,key) for (key,value) in self.dict_locs.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_locs.txt', 'w',encoding='utf-8') 
    f_out.write ("Loc\tN. Tweets\n")
    for (value,key) in locs_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_locs:
      top_size =num_locs
    for i in range (0,top_size):
      (value,loc)=locs_rank_order[i]
      self.top_locs.append(loc)
    f_out.close()
    return  

  def set_locs_day(self,date,loc):
      if loc in self.top_locs:
        index= self.top_locs.index(loc)
        self.dict_top_locs_day.store(date,index,1)
      return  

  def get_locs_day(self):     
     locs_day_matrix_order=sorted([(key,value) for (key,value) in self.dict_locs_day.items()])
     f_out=  codecs.open(self.path_experiment+self.prefix+'_locs_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date\tLoc\tCount\n")
     for  (key,value) in locs_day_matrix_order:
        (date,loc)=key
        f_out.write ('%s\t%s\t%s\t%s\t%s\n' % (loc,self.dict_locs_day[key]))
     f_out.close()
     return

  def set_words(self, text):
    words=self.token_words(text)
    for word in words:
      if word not in self.dict_stopwords:
         self.dict_words.store(word,1)
    return

  def get_words(self):
    num_words=len(self.dict_words)
    top_size=self.top_size
    print 'Num words %s' % (num_words)
    words_rank_order=sorted([(value,key) for (key,value) in self.dict_words.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_words.txt', 'w',encoding='utf-8') 
    f_out.write ("Word\tCount\n")
    for (value,key) in words_rank_order:
      f_out.write ('%s\t%s\n' % (key,value))
    f_out.close()
    if top_size > num_words:
      top_size =num_words
    for i in range (0,top_size):
      (value,word)=words_rank_order[i]
      self.top_words.append(word)
    self.write_top (self.top_words,'top_words')
    return  

  def set_words_day(self,date,text):
    words=self.token_words(text)
    for word in words:
      if word in self.top_words:
          index= self.top_words.index(word)
          self.dict_top_words_day.store(date,index,1)
    return  

  def get_words_day(self):     
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_words_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date")
     for word in self.top_words:
       f_out.write ("\t%s" % (word))
     top_size=len(self.top_words)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write ('\t%s' % (self.dict_top_words_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return

  def set_hashtags(self, text):
    words=self.token_hashtags(text)
    for word in words:
       self.dict_hashtags.store(word,1)
    return

  def get_hashtags(self):
    num_hashtags=len(self.dict_hashtags)
    top_size=self.top_size
    print 'Num hashtags %s' % (num_hashtags)
    hashtags_rank_order=sorted([(value,key) for (key,value) in self.dict_hashtags.items()],reverse=True)
    f_out=  codecs.open(self.path_experiment+self.prefix+'_hashtags.txt', 'w',encoding='utf-8') 
    f_out.write ("Hashtag\tCount\n")
    for (value,hashtag) in hashtags_rank_order:
      f_out.write ('%s\t%s\n' % (hashtag,value))
    f_out.close()
    if top_size > num_hashtags:
      top_size =num_hashtags
    for i in range (0,top_size):
      (value,hashtag)=hashtags_rank_order[i]
      self.top_hashtags.append(hashtag)
    self.write_top (self.top_hashtags,'top_hashtags')    
    return  

  def set_hashtags_day(self,date,text):
    words=self.token_hashtags(text)
    for word in words:
      if word in self.top_hashtags:
          index= self.top_hashtags.index(word)
          self.dict_top_hashtags_day.store(date,index,1)
    return  

  def get_hashtags_day(self):
     f_out=  codecs.open(self.path_experiment+self.prefix+'_top_hashtags_day.txt', 'w',encoding='utf-8') 
     f_out.write ("Date")
     for hashtag in self.top_hashtags:
       f_out.write ("\t%s" % (hashtag))
     top_size=len(self.top_hashtags)
     for (date,value) in self.tweets_day_order:
       f_out.write ('\n%s' % (date))
       for i in range (0,top_size):
          #print date,i
          f_out.write ('\t%s' % (self.dict_top_hashtags_day.getitem(date,i)))
     f_out.write ( "\n")
     f_out.close()
     return  

def get_filter (file):
    dict_filter ={}
    if os.path.isfile(file):
      f = codecs.open(file, 'rU',encoding='utf-8')
      list_words= re.findall(r'\w+',f.read(),re.U)
      for word in list_words:
        dict_filter[word]=1
    return dict_filter

def get_tweet (tweet):
   data = tweet.split('\t')
   if len (data) >= 10:
     id_tweet = data[0]
     timestamp = data[1]
     date_hour =re.findall(r'(\d\d\d\d)-(\d\d)-(\d\d)\s(\d\d):(\d\d):(\d\d)',timestamp,re.U)
     (year,month,day,hour,minutes,seconds) = date_hour[0]
     author= data[2]
     text = data[3]
     app = data[4]
     user_id = data[6]
     followers = data[6]
     following = data[7]
     statuses = data[8]
     loc = data[9]
     return (year,month,day,hour,minutes,seconds, author,text,app,user_id,followers,following,statuses,loc)
   else:
     print ' tweet not match'
     return None

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Getting entities')
  parser.add_argument('file_in', type=str, help='File with the tweets')
  parser.add_argument('path_experiment', type=str,default='', help='Dir experient')
  parser.add_argument('path_resources', type=str,default='', help='Dir experient')
  parser.add_argument('--top_size', type=str,default='10', help='Top size most importan')
  parser.add_argument('--TZ', type=str,default='0', help='offset time zone' )  
  #get arguments
  args = parser.parse_args()
  file_in= args.file_in
  path_experiment= args.path_experiment
  path_resources=args.path_resources
  top_size= int(args.top_size)
  time_setting=int(args.TZ)
  # intit data
  head=True
  first_tweet=True
  num_tweets=0
  print 'Getting entities from ',file_in
  prefix,ext=os.path.splitext(file_in)
  if ext =='':
    print "bad filename",file_in, ' Must have an extension'
    exit (1)
  try:  
    f_in = codecs.open(file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',file_in
    exit (1)
  # get start time and end time
  stopwords_file = '%sstopwords.txt' % (path_resources)
  dict_stopwords = get_filter (stopwords_file)

  counters=Counters(prefix,path_experiment,dict_stopwords,top_size)
  for line in f_in:
    if head:
      head=False
    else:
      tweet_flat= get_tweet(line)
      if tweet_flat == None:
        print 'not match '
      else:
        (year,month,day,hour,minutes,seconds, author,text,app,user_id,followers,following,statuses,loc)= tweet_flat
        text=text.lower()
        author=author.lower()
        loc=loc.lower()
        num_tweets=num_tweets +1 
        if num_tweets % 10000 == 0:
          print num_tweets  
        if first_tweet == True:
          start_time= datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minutes), second=int(seconds))
          start_day= datetime.date(year=int(year), month=int(month), day=int(day))
          first_tweet=False
        counters.set_author(author)
        counters.set_user_mention(text)
        counters.set_app(app)
        counters.set_loc(loc)
        counters.set_words(text)
        counters.set_hashtags(text)
 #end loop first pass
  end_time= datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minutes), second=int(seconds))
  end_day= datetime.date(year=int(year), month=int(month), day=int(day))
  end_hour=int(hour)
  duration=end_time-start_time
  num_days=int(duration.days)
  print  'Start time',start_time,'End time',end_time,'Total duration',duration,'days', num_days
  counters.get_authors()
  counters.get_users_RT()
  counters.get_users_reply()
  counters.get_users_mention()
  counters.get_apps()
  counters.get_locs()
  counters.get_words()
  counters.get_hashtags()
  print "segunda pasada"
  counters.reset()
  num_tweets=0
  head =True
  first_tweet = True
  f_in.seek(0) 
# Group tweets in days and get information
  for line in f_in:
    if head:
      head=False
    else:
      tweet_flat= get_tweet(line)
      if tweet_flat == None:
        print 'not match '
      else:
        (year,month,day,hour,minutes,seconds, author,text,app,user_id,followers,following,statuses,loc)=tweet_flat
        local_tz=timedelta(hours=time_setting)
        time_GMT= datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minutes), second=int(seconds))
        local_time= time_GMT + local_tz
        year=local_time.year
        month=local_time.month
        day=local_time.day
        hour=local_time.hour
        local_day= datetime.date(year=int(year), month=int(month), day=int(day))
        current_time= local_time
        current_day= local_day
        num_tweets=num_tweets +1 
        if num_tweets % 10000 == 0:
          print num_tweets  
        if first_tweet == True:
          start_time= local_time
          start_day= local_day
          last_day= current_day
          last_hour= hour
          first_tweet=False
          print 'current day',current_day
        if current_day != last_day:
          print 'current day',current_day
          last_day=current_day
        author=author.lower()
        text=text.lower()
        loc=loc.lower()
        date=current_day.strftime('%Y%m%d')
        counters.set_tweets_day(date,text)
        counters.set_authors_day(date,author)
        counters.set_user_mention_day(date,text)
        counters.set_apps_day(date,app)
        counters.set_locs_day(date,loc)
        counters.set_words_day(date,text)
        counters.set_hashtags_day(date,text)
  #end loop second pass
  counters.get_tweets_day()
  counters.get_authors_day()
  counters.get_users_RT_day()
  counters.get_users_reply_day()
  counters.get_users_mention_day()
  counters.get_apps_day()
  counters.get_words_day()
  counters.get_hashtags_day()
  f_in.close()
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
