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
import tweepy
import random
import time
import datetime
import codecs
import math
import unicodedata
import argparse

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
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

class oauth_keys(object):
  def __init__(self,  app_keys_file,user_keys_file):
    self.matrix={}
    self.app_keys_file = app_keys_file
    self.user_keys_file = user_keys_file
    self.app_keys=[]
    self.user_keys=[]
    self.dict_ratelimit={}
    try:
      f = open(self.app_keys_file, 'rU')
      for line in f: 
        self.app_keys.append(line.strip('\n'))
      f.close()
    except:
      print 'File does not exist %s' % self.app_keys_file
      exit (1)
    try:
      f = open(self.user_keys_file, 'rU')
      for line in f: 
        self.user_keys.append(line.strip('\n'))
      f.close()
    except:
      print 'File does not exist %s' % self.user_keys_file
      exit (1)
    return
    
  def get_access(self):
    try: 
      auth = tweepy.OAuthHandler(self.app_keys[0], self.app_keys[1])
      auth.set_access_token(self.user_keys[0], self.user_keys[1])
      api = tweepy.API(auth)
    except:
      print 'Error in oauth autentication, user key ', user_keys_file
      exit(83)
    return api 

  def get_rate_limits (self,api,type_resource,method,wait):
    try:
      result = api.rate_limit_status(resources=type_resource)
      resources=result['resources']
      resource=resources[type_resource]
      rate_limit=resource[method]
      limit=int(rate_limit['limit'])
      remaining_hits=int(rate_limit['remaining'])
      self.dict_ratelimit[(type_resource,method)]= remaining_hits
      while remaining_hits <1:
        print 'waiting for 5 minutes ->' + str(datetime.now())
        time.sleep(wait/3)
        result = api.rate_limit_status(resources=type_resource)
        resources=result['resources']
        resource=resources[type_resource]
        rate_limit=resource[method]
        limit=int(rate_limit['limit'])
        remaining_hits=int(rate_limit['remaining'])
        self.dict_ratelimit[(type_resource,method)]= remaining_hits
        print 'remaing hits',remaining_hits
    except:
      print 'excepction cheking ratelimit, waiting for 15 minutes ->' + time.asctime()
      print 'If the same error occurred after 15 minutes, please abort the command and check the app-user access keys'
      time.sleep(wait)
    return
 
  def check_rate_limits (self,api,type_resource,method,wait):
    if (type_resource,method) not in self.dict_ratelimit:
      self.get_rate_limits (api,type_resource,method,wait)
    else:
      self.dict_ratelimit[(type_resource,method)]-= 1
      print 'remaing hits',self.dict_ratelimit[(type_resource,method)]
      if self.dict_ratelimit[(type_resource,method)] <1 :
        self.get_rate_limits (api,type_resource,method,wait)
    return 
class what_is_my_role(object):
  def __init__(self, tweets):
    self.tweets=tweets
    self.tweets_original=[]
    self.num_tweets = len (tweets)
    print self.num_tweets
    self.num_urls_expand=0
    self.num_urls_media=0
    self.num_ht =0
    self.RT_in=0
    self.RT_out=0
    self.mentions_out=0
    self.replies_out=0
    self.dict_frecuency=AvgDict()
    self.frequency=0
    self.dict_ht=AvgDict()
    for tweet in tweets:
      #print tweet
      data=tweet.split('\t')
      #print 'len data', len(data),'data',data
      date_hour =re.findall(r'(\d\d\d\d)-(\d\d)-(\d\d)\s(\d\d):(\d\d):(\d\d)',data[1],re.U)
      (year,month,day,hour,minutes,seconds) = date_hour[0]
      date= datetime.date(year=int(year), month=int(month), day=int(day))
      self.dict_frecuency.store(date,1)
      self.user=data[2]
      #print self.user
      text=data[3]
      if type(text) != unicode:
        text=  text.decode('utf-8')
      text=text.lower()
      self.num_followers=int(data[6])
      self.num_following=int(data[7])
      self.tot_tuits=int(data[8])
      url_expand= data[10]
      url_media= data[11]
      if url_expand != 'None':
        self.num_urls_expand +=1
      if url_media != 'None':
        self.num_urls_media +=1
      relation=self.class_tweet (text)
      if relation != 'rt':
        self.tweets_original.append(tweet)
        self.RT_in += int(data[13])
    self.frequency =self.dict_frecuency.average()

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

  def get_relation(self,statuse):
    relations=[]
    list_mentions=re.findall (r'@\w+', statuse)
    if len(list_mentions) == 0:
      return('None',relations)
    else:
      if re.match(r'[\.]*(@\w+)[^\t\n]+',statuse):
        relations.append (list_mentions[0])
        return ('@', relations)
      elif re.match(r'rt (@\w+):',statuse):
        relations.append (list_mentions[0])
        #print 'RT detected'
        return ('rt',relations)
      else:  
        for mention in list_mentions:
          relations.append (mention)
        return ('mentions',relations)
    return ('None',relations)

  def class_tweet (self,text):
    # guarda tweets 
    (relation,list_relations)=self.get_relation(text)
  # guarda RT- out  
    if relation =='rt':
      self.RT_out += 1
  # guarda replies 
    elif relation =='@':
      self.replies_out +=1
    for user_dest in list_relations:
      self.mentions_out +=1
    list_ht= self.token_hashtags (text)
    for ht in list_ht:
      self.dict_ht.store (ht,1)
      self.num_ht +=1
    return relation

  def role (self):
    if self.num_tweets < 1:
      role='no tweets'
      return role
    if self.RT_out == 0:
      self.RT_out =1  #para poder calcular los coeficientes
    if self.RT_in == 0:
      self.RT_in =1  #para poder calcular los coeficientes
    own_tweets= self.num_tweets - self.RT_out
    if own_tweets <1:
      own_tweets = 1 #para poder calcular los coeficientes
    print 'tweets propios', own_tweets,len (self.tweets_original)
    print 'RT in',self.RT_in
    print 'RT out',self.RT_out
    print 'replies out',self.replies_out
    print 'mentions out',self.mentions_out
    k_rt=(self.RT_in*1.0)/self.RT_out
    k_out=(self.RT_out*1.0)/self.num_tweets
    k_in=(self.RT_in*1.0)/ own_tweets
    k_reply_out= (self.replies_out*1.0)/self.num_tweets

    #    Opinion leader (++ RT-IN)
    if  (k_in > 100):
      role='Altavoz alto'
    elif  (k_in > 10): 
      role='Altavoz medio'
    elif  (k_in > 3):
      role='Altavoz bajo' 
    #    Networking (++RT-In, ++RT-OUT)
    elif  k_rt >= 0.50:
      role='Networker' 
    elif  k_out >= 0.60:
      role='Retuiteador'
    elif  k_in <= 0.30:
      role='Monologista'
    elif  (k_reply_out >= 0.60):
      role='Replicador'
    #    Isolated ( No RT_IN no RT-OUT))
    elif (self.RT_out == 0) and (self.RT_in == 0):
      role='Aislado'
    else: 
      role='Normal'
    #print user, num_tweets,self.dict_RT_in.getitem(user),self.dict_RT_out.getitem(user),k_rt,k_in,k_out,  self.class_profile[user] 
    return role

  def gender (self):
    return

  def location (self):
    return

  def h_index (self):
    list_h=[]
    h=0
    for tweet in self.tweets_original:
      data=tweet.split('\t')
      #print 'len data', len(data),'data',data
      rts=int(data[13])
      #print rts
      list_h.append(rts)
    h_order = sorted(list_h, reverse = True)
    #print h_order
    num_h=len (h_order)
    for h in range (0,num_h):
      #print h,h_order[h]
      if h >= h_order[h]:
        break
      #print 'H-index', h
    return h 

  def ratios (self):
    if self.num_tweets < 1:
      return (0,0,0,0,0,0,0,0,0)
    if self.num_following >0:
     ratio_ff = self.num_followers *1.0/ self.num_following
    else:
     ratio_ff = 0
    try:
      ratio_RT_in = self.RT_in *1.0 / (self.num_tweets -self.RT_out -self.replies_out)
    except:
      ratio_RT_in =0
    ratio_RT_out = self.RT_out *1.0 / (self.num_tweets)
    ratio_reply_out= (self.replies_out*1.0)/self.num_tweets
    print 'RT multimedia',self.num_urls_media 
    ratio_multimedia = self.num_urls_media *1.0 / self.num_tweets
    print 'RT expand',self.num_urls_expand 
    ratio_url = self.num_urls_expand *1.0 / self.num_tweets
    ratio_ht = self.num_ht *1.0 /self.num_tweets 
    if self.num_followers >0:
      log_followers=int (math.log10(self.num_followers))
    else:
      log_followers=0
    return (ratio_ff,log_followers,ratio_RT_in,ratio_RT_out, ratio_reply_out,self.frequency,ratio_multimedia,ratio_url,ratio_ht)

  def tops (self):
    return

def get_tweets(user_keys,api,user,date_limit,f_log):  
  tweets_list=[]
  error=False
  pages=0
  print 'Getting user tweets ', user
  intentos=0
  num_pages=0
  first_tweet=True
  last_tweet=False
  recent_tweet=12345
  while  not last_tweet:
    oauth_keys.check_rate_limits (user_keys,api,'statuses','/statuses/user_timeline',900)
    try:
      if first_tweet:
        page =api.user_timeline (screen_name=user,since_id=recent_tweet,include_rts=1,count=200,include_entities=1,tweet_mode='extended')
        first_tweet=False
      else:
        page =api.user_timeline (screen_name=user,max_id=recent_tweet,include_rts=1,count=200,include_entities=1,tweet_mode='extended')
      print '--> len page', len(page)
    except:
      f_log.write(('%s, %s error en tweepy, method tweets, user %s\n')  % (time.asctime(),TypeError(),user)) 
      break
    try: 
     #page is a list of statuses
      num_pages +=1
      if len(page) <=1:
        last_tweet=True
        break
      print "--> num pages", num_pages
      for statuse in page:
        #print recent_tweet,statuse.id
        recent_tweet= statuse.id
        url_expanded =None
        geoloc=None
        location=None
        url_expanded=None
        url_media=None
        type_media=None
        text=re.sub('[\r\n\t]+', ' ',statuse.full_text)
        if statuse.entities:
        #print statuse.entities
           entities=statuse.entities
           urls=entities['urls']
           if len (urls) >0:
             url=urls[0]
             url_expanded= url['expanded_url']
             #print '\nencontrada url', url_expanded,statuse.text
        if 'media' in entities:
          list_media=entities['media']
          if len (list_media) >0:
            media=list_media[0]
            url_media= media['media_url']
            #print '\nencontrada url media', url_media,statuse.text
            type_media=media['type']
        try:
          tweet= '%s\t%s\t@%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %  (statuse.id,statuse.created_at,statuse.author.screen_name,text, statuse.source,statuse.user.id,statuse.user.followers_count,statuse.user.friends_count,statuse.user.statuses_count,location,url_expanded,url_media,geoloc, statuse.retweet_count,statuse.retweeted,statuse.in_reply_to_user_id)
          #print tweet 
          tweets_list.append(tweet)
          created_at_str= '%s' % statuse.created_at
          #print created_at_str, date_limit
          if (date_limit != None) and (created_at_str.find (date_limit) != -1):
            print 'find date_limit'
            return tweets_list
        except:
          f_log.write(('%s, %s error en tweepy, method tweets, user %s\n')  % (time.asctime(),TypeError(),user)) 
    except:
#      print 'paso por posible unicode error\n'
      text_error = '---------------> posible unicode error  at %s, id-tweet %s\n' % ( datetime.datetime.now(),statuse.id)
      f_log.write (('%s,text_error') % user)
      tweet=''
      # Catch any unicode errors while printing to console
      # and just ignore them to avoid breaking application.
      print text_error
      pass

  return tweets_list

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Main
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():

  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  start = datetime.datetime.fromtimestamp(time.time())

  result=0
  ini_key=9
  num_keys=30
  date_limit=None
  
  parser = argparse.ArgumentParser(description='This script extracts the content of a set of tweets for grouping them in days, additionally it takes note of authors, hashtag, words and specific sentences in each day.')
  
  parser.add_argument('app_key', type=str, help='keys app')
  parser.add_argument('app_user', type=str, help='Keys user')
  parser.add_argument('file_users', type=str, help='file with users list')
  args = parser.parse_args()

  app_keys_file= args.app_key
  user_keys_file= args.app_user
  users_group_file= args.file_users
  filename=re.search (r"([\w-]+)\.([\w]*)", users_group_file)
  print 'file name', users_group_file
  if not filename:
    print "bad filename",users_group_file, ' Must be an extension'
    exit (1)
  prefix=filename.group(1)
  try:
    f_users_group_file= open (users_group_file,'r')
  except:
    print 'Users group file does not exist',users_group_file 
    exit (1)   
  user_keys= oauth_keys(app_keys_file,user_keys_file)
  api= oauth_keys.get_access(user_keys)
# Open logsfile  
  f_log= open (users_group_file+'_log.txt','w')
  f_out=  codecs.open(prefix+'_role.txt','w',encoding='utf-8')
  f_out.write('User\tRole\th-index\tFollowers/Following\tlog_followers\tRatio RT_in\tRatio_RT_out\tRatio Reply_out\tFrequency\tRatio multimedia\tRatio URL\tRatio HT\n')    
  for line in f_users_group_file:
    line= line.rstrip('\r\n')
    data = line.split("\t")
    user=data[0]
    tweets= get_tweets (user_keys,api,user,None,f_log)
    whatismyrole= what_is_my_role(tweets)
    role=whatismyrole.role()
    h_index=whatismyrole.h_index()
    (ratio_ff,log_followers,ratio_RT_in,ratio_RT_out,ratio_reply_out,frequency,ratio_multimedia,ratio_url,ratio_ht) = whatismyrole.ratios()
    print  'user:', user, 'role:', role, 'h-index:',h_index
    print 'ratio ff:',ratio_ff
    print 'log_followers:',log_followers
    print 'ratio RT_in:',ratio_RT_in
    print 'ratio RT_out:',ratio_RT_out
    print 'ratio reply_out:', ratio_reply_out
    print 'frequency:',frequency
    print 'ratio multimedia:',ratio_multimedia
    print 'ratio url:',ratio_url
    print 'ratio HT:',ratio_ht
    f_out.write ('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (user,role,h_index,ratio_ff,log_followers,ratio_RT_in,ratio_RT_out,ratio_reply_out,frequency,ratio_multimedia,ratio_url,ratio_ht))
    del whatismyrole
  f_out.close()
  f_log.close()
  f_users_group_file.close()
  
  exit(0)

if __name__ == '__main__':
  main()

