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

class Taxonomy (object):
  def __init__(self, path_experiment,prefix,file_topics):
    self.prefix=prefix
    self.path_experiment=path_experiment
    self.dict_topics={}
    self.dict_count_topics=AvgDict()
    self.dict_filter={}
    try:  
      f_in = codecs.open(path_experiment+'/'+file_topics, 'rU',encoding='utf-8')
    except:
      print 'Can not open file file_topics ',self.path_experiment+'/'+file_topics
      exit (1)
    for line in f_in:
      line=line.strip("\n")
      data = line.split(":")
      topic=data[0]
      list_items=data[1].split('\t')
      for item in list_items:
        self.dict_topics[strip_accents(item)]=topic
        self.dict_count_topics[topic]=0
    f_in.close()
    file_filter='%s/filter.txt' % (self.path_experiment)
    print  self.dict_topics
    if os.path.isfile(file_filter):
      try:  
         f_in = codecs.open(path_experiment+'/'+file_filter, 'rU',encoding='utf-8')
      except:
        print 'Can not open file file_fileter ',self.path_experiment+'/'+file_filter
        exit (1)
      for line in f_in:
        line=line.strip("\n")
        line=strip_accents(line)
        self.dict_filter[line]=1
      f_in.close()
      print  self.dict_filter

class Counters(object):
  def __init__(self,prefix,path_experiment,taxonomy):
     self.prefix=prefix
     self.path_experiment=path_experiment
     self.dict_topics=taxonomy.dict_topics
     self.dict_count_topics=taxonomy.dict_count_topics
     self.dict_filter=taxonomy.dict_filter

  def pass_filter(self,text):
    for expresion in self.dict_filter:
      match = re.search(r''+ name,text,re.U)
      if match != None:
       return False
    return True

  def set_topics(self,text):
    list_topics_tweet=[]
    text=strip_accents(text)
    for token in self.dict_topics:
      if self.pass_filter(text):
        match = re.search(r''+ token,text,re.U)
        if match != None:
          topic= self.dict_topics[token]
          if topic not in list_topics_tweet:
            list_topics_tweet.append (topic)
            self.dict_count_topics.store(topic,1)
    return list_topics_tweet

  def print_tweet_topic_summary(self):
    f_out = codecs.open(self.path_experiment+'/'+self.prefix+'_summary_topics.txt', 'w',encoding='utf-8')
    f_out.write('Topic\tN. tweets\n')
    for topic in self.dict_count_topics:
      print '%s\t%s' % (topic,self.dict_count_topics.getitem(topic))
      f_out.write ('%s\t%s\n' % (topic,self.dict_count_topics.getitem(topic)))
    f_out.close()
    return

def get_tweet (tweet):
   data = tweet.split('\t')
   if len (data) >= 4:
     id_tweet = data[0]
     timestamp = data[1]
     date_hour =re.findall(r'(\d\d\d\d)-(\d\d)-(\d\d)\s(\d\d):(\d\d):(\d\d)',timestamp,re.U)
     (year,month,day,hour,minutes,seconds) = date_hour[0]
     author= data[2]
     text = data[3]
     return (id_tweet,year,month,day,hour,minutes,seconds, author,text)
   else:
     print ' tweet not match'
     return None

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  parser = argparse.ArgumentParser(description='This script classifies tweets according to topics')
  parser.add_argument('file_in', type=str, help='file with raw tweets')
  parser.add_argument('file_topics', type=str, help='file with topics dictionary')
  parser.add_argument('path_experiment', type=str,default='', help='Dir experient')
  args = parser.parse_args()
  file_in=args.file_in
  file_topics=args.file_topics
  path_experiment=args.path_experiment
# intit data
  head=True
  first_tweet=True
  num_tweets=0
  prefix,ext=os.path.splitext(file_in)
  if ext =='':
    print "bad filename",file_in, ' Must have an extension'
    exit (1)
  prefix_topics,ext_topics=os.path.splitext(file_topics)
  if ext =='':
    print "bad filename",file_in, ' Must have an extension'
    exit (1)
  try:  
    f_in = codecs.open(path_experiment+'/'+file_in, 'rU',encoding='utf-8',errors='ignore')
  except:
    print 'Can not open file',path_experiment+'/'+file_in
  f_out = codecs.open(path_experiment+'/'+prefix+'_topics.txt', 'w',encoding='utf-8')
  taxonomy=Taxonomy(path_experiment,prefix, file_topics)
  counters=Counters(prefix,path_experiment,taxonomy)
  for line in f_in:
    if head:
      head=False
      f_out.write ('%s\tTopics\n' % (line))
    else:
      tweet_flat= get_tweet(line)
      if tweet_flat == None:
        print 'not match '
      else:
        (id_tweet,year,month,day,hour,minutes,seconds, author,text)= tweet_flat
        if num_tweets % 10000 == 0:
          print num_tweets  
        num_tweets=num_tweets +1 
        author=author.lower()
        text=text.lower()
        list_topics= counters.set_topics(text)
        f_out.write ('%s\t%s\n' % (line,list_topics))
  counters.print_tweet_topic_summary()
  f_in.close()
  f_out.close()
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)

 