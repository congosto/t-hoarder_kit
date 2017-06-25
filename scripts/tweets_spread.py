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
#from datetime import datetime,date
import socket
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
class Matrix(object):
  def __init__(self,  rows,cols):
    self.matrix={}
    self.cols = int(cols)
    self.rows = int(rows)

  def setitem(self, row, col, v):
    self.matrix[row-1,col-1]=v
    return

  def getitem(self, row,col):
    if (row-1,col-1) not in self.matrix:
      return 0
    else:
      return self.matrix[row-1,col-1]

  def __iter__(self):
    for row in range(self.rows):
      for col in range(self.cols):
        yield (self.matrix, row, col) 

  def __repr__(self):
    outStr = ""
    for i in range(self.rows):
      for j in range(self.cols):
        if (i,j) not in self.matrix:
          outStr += '0.00,'
        else: 
          outStr += '%.2f,' % ( self.matrix[i,j])
      outStr += '\n'  
    return outStr      

# # A dictionary 

class Rank(object):
  def __init__(self):
    self.rank={}

  def set_item(self, item,value):
    if item not in self.rank:
      self.rank[item] = value
    else:
      self.rank[item] = self.rank[item] +value     
    return

  def get_item(self, item):
    if item in self.rank:
      return  self.rank[item]
    else:
      return 0

  def get_top_frequency(self, min_frequency):
    self.rank_order=sorted([(value,key) for (key,value) in self.rank.items()],reverse=True)
    for i in range (0,len (self.rank_order)):
      (value,key) = self.rank_order[i]
      if value < min_frequency:
        del self.rank_order[i:]
        break
    return self.rank_order
 
  def get_top_number(self, min_frequency,mun_elements):
    self.rank_order=sorted([(value,key) for (key,value) in self.rank.items()],reverse=True)
    del self.rank_order[num_elements:]
    return self.rank_order

# # Sentences similarity 
class Sentence_similarity (object):
  def __init__(self,path_experiment,prefix,size_sentences):
    self.size_sentences=size_sentences
    self.path_experiment=path_experiment
    self.prefix=prefix
    self.rank={}
    self.list_texts=[]
    self.dict_id_tweets={}
    self.dict_sentences={}
    self.dict_sentences_count={}
    self.dict_date={}
    self.last_sentence_day =0

 
  def set_item(self, words,text_source,author,author_source,date,id_tweet):
    found = False
    set_words = frozenset(words) 
    len_set_words = len ( set_words )
    if author_source==None:  #new sentence  
      #print 'new sentence'   
      self.list_texts.append((text_source,author)) 
      self.dict_id_tweets[text_source,author]=id_tweet
      self.dict_sentences[text_source,author]=words
      self.dict_sentences_count[text_source,author]=1
      self.dict_date [text_source,author]=date
      return
    else: #find similarity
      for (text,author_actual)  in self.list_texts:
        if author_source == author_actual: 
          sentence=self.dict_sentences[text,author_actual]
          set_sentence = frozenset(sentence)
          if (abs((len_set_words) - len (set_sentence))) < 4:
            if (len (set_words & set_sentence)/float(len_set_words)) > 0.9 :
              self.dict_sentences_count[text,author_actual] += 1        
              found = True
              break
      if not found:  #Maybe a RT with out original tweet  
        self.list_texts.append((text_source,author_source)) 
        self.dict_id_tweets[text_source,author_source]=id_tweet
        self.dict_sentences[text_source,author_source]=words
        self.dict_sentences_count[text_source,author_source]=1
        self.dict_date [text_source,author_source]=date
    return   
  
  def set_hour(self):   
       #remove sentences not frequent
    list_texts_aux=[]   
    dict_id_tweets_aux={}
    dict_sentences_aux={}
    dict_sentences_count_aux={}
    dict_date_aux={}
    sentences_rank_order=sorted([(value,key) for (key,value) in self.dict_sentences_count.items()],reverse=True) 
    num_sentences=0
    for (value,key) in sentences_rank_order:
      (text, author)=key
      num_sentences += 1
      if num_sentences > (self.size_sentences * 2):
        break
      list_texts_aux.append((text,author))
      dict_id_tweets_aux[text,author]= self.dict_id_tweets[text,author]
      dict_sentences_aux[text,author] = self.dict_sentences[text,author]
      dict_sentences_count_aux[text,author] = self.dict_sentences_count[text,author]
      dict_date_aux[text,author] =self. dict_date[text,author]
    self.list_texts[:]
    self.dict_id_tweets.clear()
    self.dict_sentences.clear()
    self.dict_sentences_count.clear()
    self.dict_date.clear()
    self.list_texts = list_texts_aux
    self.dict_id_tweets=dict_id_tweets_aux  
    self.dict_sentences = dict_sentences_aux
    self.dict_sentences_count = dict_sentences_count_aux
    self.dict_date = dict_date_aux
    print 'Num sentences stored', len(self.list_texts)    , len(self.dict_sentences_count)
    return 
    
  def set_day(self,day):   
    #remove sentences not frequent
    list_texts_aux=[]  
    dict_id_tweets_aux={}
    dict_sentences_aux={}
    dict_sentences_count_aux={}
    dict_date_aux={}
    print 'set day', day, len(self. dict_sentences)
    sentences_rank_order=sorted([(value,key) for (key,value) in self.dict_sentences_count.items()],reverse=True) 
    num_sentences=0
    for (value,key) in sentences_rank_order:
      (text, author)=key
      num_sentences += 1
      if num_sentences > self.size_sentences:
        break
      list_texts_aux.append((text,author))
      dict_id_tweets_aux[text,author]= self.dict_id_tweets[text,author]
      dict_sentences_aux[text,author] = self.dict_sentences[text,author]
      dict_sentences_count_aux[text,author] = self.dict_sentences_count[text,author]
      dict_date_aux[text,author] =self. dict_date[text,author]
    self.list_texts[:]
    self.dict_id_tweets.clear()
    self.dict_sentences.clear()
    self.dict_sentences_count.clear()
    self.dict_date.clear()
    self.list_texts = list_texts_aux
    self.dict_id_tweets=dict_id_tweets_aux 
    self.dict_sentences = dict_sentences_aux
    self.dict_sentences_count = dict_sentences_count_aux
    self.dict_date= dict_date_aux
    print 'Num sentences stored', len(self.list_texts)   , len(self.dict_sentences_count)
    return 

  def get_sentences(self):
    return self.dict_sentences

  def get_sentences_count (self):
    return self.dict_sentences_count

  def get_texts (self):
    return  self.list_texts

  def get_id_tweets (self):
    return  self.dict_id_tweets

  def get_num_sentences (self):  
    return len(self.list_texts)

  def get_dict_date (self):  
    return self.dict_date

  def get_dict_sentences (self):  
    return self.dict_sentences
   
  def reset_sentences (self):  
    print 'cleaned day'
    self.rank.clear()
    self.list_texts[:]
    self.dict_authors.clear()
    self.dict_sentences.clear()
    self.dict_sentences_count.clear()
    self.list_texts[:]
    self.last_sentence_day =0
    return 

  def set_context(self,current_day,line,byte):
    f_last_day= codecs.open(self.path_experiment+'/'+self.prefix+'_last_day.txt', 'w',encoding='utf-8')
    f_last_day.write('%s\t%s\t%s\n' % ( current_day,line,byte))
    f_last_day.close()    
    return 

  def put_store(self,type_store):
    f_sentences= codecs.open(self.path_experiment+'/'+self.prefix+type_store+'.txt', 'w',encoding='utf-8')
    for (text,author) in self.list_texts:
      f_sentences.write('%s\t%s\t%s\t%s\t%s\n' % ( text,author, self.dict_sentences_count[text,author],self.dict_date [text,author],self.dict_id_tweets[text,author]))
    f_sentences.close()
    return

def token_words_url (source):
  list_words=[]

#  print '\nafter remove urls\n',source_with_out_urls.encode( "utf-8" ) 
  list_tokens=re.findall (r'\S+', source,re.U) 
#  remove users and rts
  for token in list_tokens:
    #if  (token.find(u'@') == -1):
    #  token=token.lower()
    if (token != u'rt') and (token !=u'vía') and (token != u'via'):
      list_words.append(token)
  return list_words  

def get_tweet_source (text):
  source=None
  text_aux=text
  start=text_aux.find('RT')
  while  start !=  -1:
    #print start
    text=text_aux[start:]
    #print text
    RT = re.match('[RT[\s]*(@\w+)[:]*',text,re.U)
    if RT:
      source=RT.group(1)
      text_aux=text[len(RT.group(0)):]
      #print text_aux
      #print source
      start=text_aux.find('RT')
    else:
      break
  return (source, text_aux)

def get_ranges(taglist,size_list):
  ranges = []
  #print len(taglist),size_list
  if len(taglist) >0:
    (count,index)=taglist[0]
    maxcount = count
    (count,index)=taglist[size_list-1]
    mincount = count
    distrib = (maxcount - mincount+3)/ 4;
    index = mincount
    if distrib >0:
      while (index <= maxcount):
        range = (index, index + distrib)
        index = index + distrib
        ranges.append(range)
    else:
        range=(1,1)
        ranges.append(range)   
  return ranges  

def  print_cloud_sentences_global (path_experiment,dict_date,rank_sentences,dict_id_tweets,size_sentences,prefix,name_file): 
  num_pag= (size_sentences+3)/4
  ranges=get_ranges(rank_sentences,size_sentences) 
  #print ranges    
  f_out_csv = codecs.open(name_file, 'w',encoding='utf-8')
  num_sentences=0
  page=0
  for (count,tweet) in rank_sentences:
    (text,author)=tweet
    author_sin=author[1:]
    id_tweet=dict_id_tweets[text,author]
    if num_sentences > size_sentences:
      break
    f_out_csv.write (('%s\t%s\t%s\t%s\t%s\n') % (dict_date[text,author],author,text,count,id_tweet))
    num_sentences = num_sentences + 1  
  f_out_csv.close()
  return  


def clean_output_files(output_file_name):
  command='rm %s\n' % (output_file_name)
  print command
  os.system(command) 
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
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Getting spread')
  parser.add_argument('file_in', type=str, help='File with the tweets')
  parser.add_argument('path_experiment', type=str,default='', help='Dir experient')
  parser.add_argument('--top_size', type=str,default='1000', help='Top size most importan')
  parser.add_argument('--TZ', type=str,default='0', help='offset time zone' )  
  #get arguments
  args = parser.parse_args()
  file_in= args.file_in
  path_experiment= args.path_experiment
  max_sentences= int(args.top_size)
  time_setting=int(args.TZ)
  
# intit data
  first_tweet=True
  head=True
  tweets=0
  num_tweets=0
  max_tweet_hour = 15000
  max_sentences_print= 1000
  max_sentences_print_day = 500
  list_dates_str=[]
# proccess
  filename=re.search (r"([\w-]+)\.([\w]*)", file_in)
  print 'file name', file_in
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  name=filename.group(0)
  prefix=filename.group(1)
  try:  
    f_in = codecs.open(path_experiment+file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',path_experiment+file_in
    exit (1)
  sentences= Sentence_similarity(path_experiment,prefix,max_sentences)
  sentences_day=Sentence_similarity(path_experiment,prefix,max_sentences)
  for line in f_in:
    if head:
      head=False
    else:
      tweet_flat= get_tweet(line)
      if tweet_flat == None:
        print 'not match '
      else:
        (id_tweet,year,month,day,hour,minutes,seconds, author,text)= tweet_flat
        if num_tweets % 10000 == 0:
          print num_tweets  
        num_tweets=num_tweets +1 
        local_tz=timedelta(hours=time_setting)
        time_GMT= datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minutes), second=int(seconds))
        local_time= time_GMT + local_tz
        year=str(local_time.year)
        month=str(local_time.month)
        day=str(local_time.day)
        hour=str(local_time.hour)
        local_day= datetime.date(year=int(year), month=int(month), day=int(day))
        date=year+'/'+month+'/'+day+' '+hour+':'+minutes+':'+seconds
        current_day=datetime.date(year=int(year), month=int(month), day=int(day))
        (author_source,text_source) = get_tweet_source (text)
        if first_tweet == True:
          start_time= datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minutes), second=int(seconds))
          start_day= current_day
          start_hour=hour
          first_tweet=False
          last_day=current_day
          last_hour=hour
          tweets_hour =0
        tweets_hour= tweets_hour +1
        end_day= datetime.date(year=int(year), month=int(month), day=int(day))
        if tweets_hour > max_tweet_hour:
          print 'day', day, 'hour', hour, 'tweets hour', tweets_hour,'block hour'
          sentences.set_hour()
          sentences_day.set_hour()
          tweets_hour =0
        if hour != last_hour:
          print 'day', day, 'hour', hour, 'tweets hour', tweets_hour
          sentences.set_hour()
          sentences_day.set_hour()
          tweets_hour =0
          last_hour=hour
         #print ' change day',current_day,last_day
        if current_day != last_day: 
          sentences.set_day(last_day)
          sentences_day.set_day(last_day)
          list_texts = sentences_day.get_texts()
          dict_id_tweets= sentences_day.get_id_tweets ()
          dict_sentences_count = sentences_day.get_sentences_count()
          dict_date=sentences_day.get_dict_date()
          num_sentences= len(list_texts)
          print num_sentences, len (dict_sentences_count)
          if num_sentences > max_sentences_print_day:
            num_sentences= max_sentences_print_day
          sentences_rank_order=sorted([(value,key) for (key,value) in dict_sentences_count.items()],reverse=True) 
          day_str= str(last_day)
          list_dates_str.append(day_str)
          print_cloud_sentences_global (path_experiment,dict_date,sentences_rank_order,dict_id_tweets,num_sentences,prefix,path_experiment+prefix+'_'+day_str+'_sentences.csv')
          #sentences_day.reset_sentences()
          sentences_day=Sentence_similarity(path_experiment,prefix,max_sentences)
          last_day=current_day
          #store similar tweets   
        if last_day==current_day: #ignore tweets not order
          words= token_words_url (text_source)
          set_words= frozenset(words)
          len_set_words=len (set_words)
          if len(words) >=7 and (author != author_source):
            sentences.set_item(words,text_source,author,author_source,date,id_tweet)
            sentences_day.set_item(words,text_source,author,author_source,date,id_tweet)
            #find similarity
     
  #remove sentences not frequent
  sentences.set_hour()
  sentences.set_day(current_day)
  sentences_day.set_day(current_day)
  f_in.close()     
  #finish geting tweets 
  list_texts = sentences_day.get_texts()
  dict_id_tweets= sentences_day.get_id_tweets ()
  dict_sentences_count = sentences_day.get_sentences_count()
  dict_date=sentences_day.get_dict_date()
  num_sentences= len(list_texts)
  print num_sentences, len (dict_sentences_count)
  if num_sentences > max_sentences_print_day:
   num_sentences= max_sentences_print_day
  day_str= str(last_day)
  sentences_rank_order=sorted([(value,key) for (key,value) in dict_sentences_count.items()],reverse=True) 
  print_cloud_sentences_global (path_experiment,dict_date,sentences_rank_order,dict_id_tweets,num_sentences,prefix,path_experiment+prefix+'_'+day_str+'_sentences.csv')

  list_texts = sentences.get_texts()
  dict_id_tweets= sentences.get_id_tweets ()
  dict_sentences_count = sentences.get_sentences_count()
  dict_date=sentences.get_dict_date()
  num_sentences= len(list_texts)
  if num_sentences > max_sentences_print:
    num_sentences=max_sentences_print
  sentences_rank_order=sorted([(value,key) for (key,value) in dict_sentences_count.items()],reverse=True) 
  print_cloud_sentences_global (path_experiment,dict_date, sentences_rank_order,dict_id_tweets,num_sentences,prefix,path_experiment+prefix+'_global_sentences.csv')
  last_line_last_day = num_tweets
  sentences.put_store('_last_global_sentences')
  sentences_day.put_store('_last_day_sentences')
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
