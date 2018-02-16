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

class TweetsActivity(object):
  def __init__(self, prefix):
    self.prefix=prefix
    self.tweets=AvgDict()
    self.tweets_by_day=Matrix()
    self.days=[]
    self.dict_RT_in=AvgDict()
    self.dict_RT_out=AvgDict()
    self.dict_mentions_in=AvgDict()
    self.dict_mentions_out=AvgDict()
    self.dict_replies_in=AvgDict()
    self.dict_replies_out=AvgDict()
    self.dict_RT_in_uniq=AvgDict()
    self.dict_RT_out_uniq=AvgDict()
    self.dict_mentions_in_uniq=AvgDict()
    self.dict_mentions_out_uniq=AvgDict()
    self.dict_replies_in_uniq=AvgDict()
    self.dict_replies_out_uniq=AvgDict()
    self.dict_RT_in_par=Matrix()
    self.dict_RT_out_par=Matrix()
    self.dict_mentions_in_par=Matrix()
    self.dict_mentions_out_par=Matrix()
    self.dict_replies_in_par=Matrix()
    self.dict_replies_out_par=Matrix()
    self.num_users=0
    self.num_tweets=0
    self.num_RTs=0
    self.num_mentions=0
    self.num_replies=0
    self.class_profile={}

  def get_relation(self,statuse):
    relations=[]
    list_mentions=re.findall (r'@\w+', statuse)
    if len(list_mentions) == 0:
      return('None',relations)
    else:
      if re.match(r'[\.]*(@\w+)[^\t\n]+',statuse):
        relations.append (list_mentions[0])
        return ('@', relations)
      elif (statuse.find('rt ') != -1):
        relations.append (list_mentions[0])
        return ('rt',relations)
      else:  
        for mention in list_mentions:
          relations.append (mention)
        return ('mentions',relations)

  def class_tweet (self,user,text):
    self.num_users +=1
    self.num_tweets +=1
    # guarda tweets por usuario
    self.tweets.store(user,1)
    # guarda tweets por usuario y dia
    (relation,list_relations)=self.get_relation(text)
  # guarda RT-in /RT- out por usuario 
    if relation =='rt':
      self.num_RTs +=1
      user_dest=list_relations[0]
      self.dict_RT_in.store(user_dest,1)
      self.dict_RT_out.store(user,1)
      if  self.dict_RT_in_par.getitem(user_dest,user) ==0:
        self.dict_RT_in_uniq.store(user_dest,1)
        self.dict_RT_in_par.store_unique (user_dest, user,1)
      if  self.dict_RT_out_par.getitem(user,user_dest) ==0:
        self.dict_RT_out_uniq.store(user,1)
        self.dict_RT_out_par.store_unique (user,user_dest,1)
  # guarda replies por usuario
    elif relation =='@':
      self.num_replies +=1
      user_dest=list_relations[0]
      self.dict_replies_in.store(user_dest,1)
      self.dict_replies_out.store(user,1)
      if  self.dict_replies_in_par.getitem(user_dest,user) ==0:
        self.dict_replies_in_uniq.store(user_dest,1)
        self.dict_replies_in_par.store_unique (user_dest, user,1)
      if  self.dict_replies_out_par.getitem(user,user_dest) ==0:
        self.dict_replies_out_uniq.store(user,1)
        self.dict_replies_out_par.store_unique (user,user_dest,1)
    for user_dest in list_relations:
      self.num_mentions +=1
      self.dict_mentions_in.store(user_dest,1)
      self.dict_mentions_out.store(user,1)
      if  self.dict_mentions_in_par.getitem(user_dest,user) ==0:
        self.dict_mentions_in_uniq.store(user_dest,1)
        self.dict_mentions_in_par.store_unique (user_dest, user,1)
      if  self.dict_mentions_out_par.getitem(user,user_dest) ==0:
        self.dict_mentions_out_uniq.store(user,1)
        self.dict_mentions_out_par.store_unique (user,user_dest,1)
    return

  def RTs (self, user):
    return (self.dict_RT_in.getitem(user),self.dict_RT_out.getitem(user))

  def RTs_uniq (self, user):
    return (self.dict_RT_in_uniq.getitem(user),self.dict_RT_out_uniq.getitem(user))

  def replies (self, user):
    return (self.dict_replies_in.getitem(user),self.dict_replies_out.getitem(user)) 

  def replies_uniq (self, user):
    return (self.dict_replies_in_uniq.getitem(user),self.dict_replies_out_uniq.getitem(user)) 

  def mentions (self, user):
    return (self.dict_mentions_in.getitem(user),self.dict_mentions_out.getitem(user)) 

  def mentions_uniq(self, user):
    return (self.dict_mentions_in_uniq.getitem(user),self.dict_mentions_out_uniq.getitem(user)) 

  def tweets_user (self, user):
    return (self.tweets.getitem(user)) 

  def get_tops (self,dict_data, total,percentage):
    top=(total* percentage *1.0) /100 
    list_order=sorted([(value,key) for (key,value) in dict_data.items()],reverse=True)
    list_top=[]
    value_accumulated=0
    for (value,user)  in list_order:
      #print top,value, value_accumulated
      list_top.append(user)
      #print user,'RTs_in',value, 'top',top
      value_accumulated += value
      if value_accumulated > top:
        break
    #print list_top
    return list_top

  def perfil (self, user):
    #  perfil
    if self.dict_RT_out.getitem(user) == 0:
      self.dict_RT_out.store(user,1)  #para poder calcular los coeficientes
    elif self.tweets.getitem(user) ==0:
      self.tweets.store(user,1) #para poder calcular coeficientes
    num_tweets= self.tweets.getitem (user)
    average_tweets=self.tweets.average ()
    rts_out=self.dict_RT_out.getitem(user)
    rts_in=self.dict_RT_in.getitem(user)
    own_tweets=num_tweets-rts_out+1
    k_rt=(self.dict_RT_in.getitem(user)*1.0)/self.dict_RT_out.getitem(user)
    k_out=(self.dict_RT_out.getitem(user)*1.0)/num_tweets
    k_in=(self.dict_RT_in.getitem(user)*1.0)/ own_tweets
    k_reply_out= (self.dict_replies_out.getitem(user)*1.0)/ own_tweets
    average_RT_out=self.dict_RT_out.average()
    average_RT_in=self.dict_RT_in.average()
      #    Opinion leader (++ RT-IN)
    #print self.list_top_20 , self.list_top_50
    if  (k_in > 3) and user in self.list_top_20: 
        self.class_profile[user]='Altavoz alto'
    elif  (k_in > 3) and user in self.list_top_50: 
        self.class_profile[user]='Altavoz medio'
    elif  (k_in > 3):
        self.class_profile[user]='Altavoz bajo'   
    #    transmitter (++RT-OUT)
    #    Networking (++RT-In, ++RT-OUT)
    elif  (num_tweets >= average_tweets) and  (k_out >= 0.50):
      self.class_profile[user]='Retuiteador'
    elif  (num_tweets >= average_tweets) and (k_in <= 0.30):
      self.class_profile[user]='Monologista'
    elif  (k_reply_out >= 0.60):
      self.class_profile[user]='Replicador'
    elif (num_tweets >= average_tweets) and (rts_in >= average_RT_in)  and (k_rt >= 0.50):
      self.class_profile[user]='Networker' 
    elif (self.dict_RT_out.getitem(user) == 0) and (self.dict_RT_in.getitem(user) == 0):
    #    Isolated ( No RT_IN no RT-OUT))
      self.class_profile[user]='Aislado'
    else: 
      self.class_profile[user]='Normal'
    #print user, num_tweets,self.dict_RT_in.getitem(user),self.dict_RT_out.getitem(user),k_rt,k_in,k_out,  self.class_profile[user] 
    return self.class_profile[user]

  def get_media(self):
    self.list_top_20= self.get_tops(self.dict_RT_in,self.num_RTs,20)
    self.list_top_50= self.get_tops(self.dict_RT_in,self.num_RTs,50)
    print 'Average tweets per user %.2f' % self.tweets.average()
    print 'Average RTs_in per user %.2f' % self.dict_RT_in.average()
    print 'Average RTs_out per user %.2f'% self.dict_RT_out.average()
    print 'Average replies_in_out per user %.2f' % self.dict_replies_in.average()
    print 'Average replies_out_out per user %.2f' % self.dict_replies_out.average()
    return

def get_tweet (tweet):
   data = tweet.split('\t')
   try:
     id_tweet = data[0]
     timestamp = data[1]
     date_hour =re.findall(r'(\d\d\d\d)-(\d\d)-(\d\d)\s(\d\d):(\d\d):(\d\d)',timestamp,re.U)
     (year,month,day,hour,minutes,seconds) = date_hour[0]
     author= data[2]
     text = data[3]
     app = data[4]
     id_user = data[5]
     followers = data[6]
     following = data [7]
     return (id_tweet,year,month,day,hour,minutes,seconds, author,text,app,id_user,followers,following)
   except:
     print ' tweet not match'
     return None

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  parser = argparse.ArgumentParser(description='ls this script classifies users into categories according to their activity')
  parser.add_argument('file_in', type=str, help='file with raw tweets')
  parser.add_argument('path_experiment', type=str,default='', help='Dir experient')
  args = parser.parse_args()
  file_in=args.file_in
  path_experiment=args.path_experiment
  dict_users={}
# intit data
  #get parameters
  flag_users=False
  head=True
  num_tweets=0
  first_tweet=True

  prefix,ext=os.path.splitext(file_in)
  if ext =='':
    print "bad filename",file_in, ' Must have an extension'
    exit (1)
  activity= TweetsActivity(prefix)
  #analize Tweets
  try:  
    f_in = codecs.open(path_experiment+'/'+file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',file_in
    exit (1)
  f_out = codecs.open(path_experiment+'/'+prefix+'_roles.txt', 'w',encoding='utf-8') 
  f_out.write('user\trole\tinf_ff\tlog_ff\trts_in\trts_out\trts_in_uniq\trts_out_uniq\treplies_in\treplies_out\treplies_in_uniq\treplies_out_uniq\tmentions_in\tmentions_out\tmentions_in_uniq\tmentions_out_uniq\n')
  for line in f_in:
    if head:
      head=False
    else:
      tweet_flat= get_tweet(line)
      if tweet_flat == None:
        print 'not match '
      else:
        if num_tweets % 10000 == 0:
          print num_tweets 
        num_tweets += 1
        (id_tweet,year,month,day,hour,minutes,seconds, author,text,app,user_id,followers,following)=tweet_flat
        author=author.lower()
        text=text.lower()
        if float(following) !=0:
          ind_ff=float(followers)/float(following)
        else:
          ind_ff=0
        if int(followers) !=0:
          log_followers=int(math.log(float(followers),10))
        else:
          log_followers=1
        dict_users[author]=((ind_ff,log_followers))
        activity.class_tweet (author,text)
  activity.get_media () 
  for user  in dict_users:
    (ind_ff,log_followers)=dict_users[user]
    perfil=activity.perfil(user)
    f_out.write('%s\t%s\t%.2f\t%s' % (user,perfil,ind_ff,log_followers))
    num_tweets= activity.tweets_user (user)
    (RT_in,RT_out)= activity.RTs (user)
    f_out.write('\t%s\t%s' % (RT_in,RT_out))
    (RT_in_uniq,RT_out_uniq) = activity.RTs_uniq (user)
    f_out.write('\t%s\t%s' % (RT_in_uniq,RT_out_uniq))
    (replies_in,replies_out) = activity.replies (user)
    f_out.write('\t%s\t%s' % (replies_in,replies_out))
    (replies_in_uniq,replies_out_uniq) = activity.replies_uniq (user)
    f_out.write('\t%s\t%s' % (replies_in_uniq,replies_out_uniq))
    (mentions_in,mentions_out) = activity.mentions (user)
    f_out.write('\t%s\t%s' % (mentions_in,mentions_out))
    (mentions_in_uniq,mentions_out_uniq) = activity.mentions_uniq (user)
    f_out.write('\t%s\t%s\n' % (mentions_in_uniq,mentions_out_uniq))
  f_in.close()
  f_out.close()
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
