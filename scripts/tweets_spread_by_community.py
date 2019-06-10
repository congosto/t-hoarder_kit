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
import codecs
import argparse

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


def set_RTs_day_community(date,author):
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

def get_tweet (line):
   line= line.strip('\n\r')
   data=line.split('\t')
   #if True:
   try:
     id_tweet = data[0]
     date=data[1]
     author= data[2]
     text = data[3]
     relation=data[17]
     if relation =='RT':
       index=text.find (':')
       text= text[index:]
     tweet_id_retweeted=data[20]
     user_retweeted= data[21]
     i=len(data)-1
     community=data[i]
     return (id_tweet,date,author,text,relation,tweet_id_retweeted,user_retweeted,community)
   #else:
   except:
     print ' tweet not match', line
     return (None,None,None,None,None,None,None,None)

def get_community (file):
    list_community =[]
    f = codecs.open(file, 'rU',encoding='utf-8')
    for line in f:
       line= line.strip('\n\r')
       data=line.split('\t')
       num_community=data[0]
       name_community=data[1]
       list_community.append ((num_community,name_community))
    return list_community
def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Examples usage Twitter API REST, search method')
  parser.add_argument('file_in', type=str, help='name file in with id_tweet')
  parser.add_argument('--dir_out', type=str, default='./', help='Dir data output')
  parser.add_argument('--community', type=str,  help='file community')
  parser.add_argument('--top', type=str, default='50', help='top for summary')
  #obtego los argumentos
  args = parser.parse_args()
  file_in= args.file_in
  dir_out=args.dir_out
  file_community=args.community
  top= int(args.top)
  dict_tweets={}
  dict_RTs_count= AvgDict()
  dict_RTs_count_community=Matrix()
  list_communities=[]
  file_base=os.path.basename(file_in)
  (prefix,text)=os.path.splitext(file_base)
  try:
    f_in = codecs.open(file_in, 'rU',encoding='utf-8')
    print 'open as unicode'
  except:
    print 'Can not open file',file_in
    exit (1)
  f_log= open(dir_out+'/'+prefix+'.log','w')
  head=True
  n_tweets=0
  list_community=get_community (file_community)
  for line in f_in:
    if (n_tweets % 10000) == 0:
      print n_tweets
    n_tweets +=1
    if head:
      head=False
    else:
     (id_tweet,date,author,text,relation,tweet_id_retweeted,user_retweeted,community) = get_tweet (line)
     if relation == 'None':
       dict_tweets[id_tweet]=(id_tweet,date,author,text,relation,tweet_id_retweeted,user_retweeted,community)
     if (relation == 'RT') and (community != 'None'):
       if id_tweet not in dict_tweets:
         dict_tweets[tweet_id_retweeted]=(id_tweet,date,author,text,relation,tweet_id_retweeted,user_retweeted,community)
       dict_RTs_count.store(tweet_id_retweeted,1)
       dict_RTs_count_community.store(community,tweet_id_retweeted,1)
  for (num_community,name_community) in list_community:
    print 'Get %s community' % (name_community)
    f_out=  codecs.open(dir_out+'/'+prefix+'_spread_'+name_community+'.txt','w',encoding='utf-8')
    dict_RT_aux={}
    for (num_community_aux,tweet_id_tweet) in dict_RTs_count_community:
      #print num_community_aux, num_community 
      if num_community_aux == num_community:
        dict_RT_aux[tweet_id_tweet]= dict_RTs_count_community.getitem(num_community_aux,tweet_id_tweet)
    RTs_rank_order=sorted([(value,key) for (key,value) in dict_RT_aux.items()],reverse=True)
    i=0
    for (value,key) in   RTs_rank_order:
      (id_tweet,date,author,text,relation,tweet_id_retweeted,user_retweeted,community)=dict_tweets[key]
      if author != user_retweeted:
        author = user_retweeted
        if_tweet= tweet_id_retweeted
      f_out.write (('%s\t%s\t%s\t%s\t%s\thttps://twitter.com/%s/statuses/%s\n') % (date,user_retweeted,text,value,id_tweet,author,id_tweet))
      if i > top:
        break
      i += 1
    f_out.close ()
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
