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
import unicodedata
import codecs
import math
import argparse
#  
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
        retur

# # A dinamic matrix
# # This matrix is a dict whit only cells it nedeed
# # 
#  
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
    
class Relation(object):
  def __init__(self,  prefix,top_size, relation):
     self.prefix=prefix
     self.dict_authors={}
     self.top_size = top_size
     self.relation= relation
     self.dict_users=AvgDict()
     self.dict_in=AvgDict()
     self.dict_out=AvgDict()
     self.dict_links=AvgDict()
     self.dict_rank_links={}
     self.dict_rank_links_index={}
     self.dict_tweets=AvgDict()
     self.top_authors=AvgDict()
     self.top_mentions=AvgDict()
     self.top=AvgDict()
     self.top_matrix=Matrix()
     self.most_mentions_matrix=Matrix()
     return
     
  def set_author(self, author,info_author):
    self.dict_authors[author]= info_author
    self.dict_tweets.store_unique(author,1)
    return
    
  def get_relation(self,text,relation):
    relations=[]
    list_mentions=re.findall (r'@\w+', text)
    if len (list_mentions) >0:
      if relation =='reply':
        if re.match(r'[\.]*(@\w+)[^\t\n]+',text):
          relations.append (list_mentions[0])
        return relations
      if relation=='RT':
        if re.match('rt @\w+:',text):
          relations.append (list_mentions[0])
        return relations
      if relation=='mention':     
        for mention in list_mentions:
          relations.append (mention)
      print relations
    return relations
  
  def set_relation(self, author,text,list_relations,relation):
     num_mentions=  len (list_relations)
     self.dict_out.store(author,num_mentions)
     self.dict_links.store(author,num_mentions)
     for user in list_relations:
       self.dict_in.store(user,1)
       self.dict_links.store(user,1)
     return     
  
  def get_top_authors (self):
    self.authors_rank_order=sorted([(value,key) for (key,value) in self.dict_tweets.items()],reverse=True)
    num_authors=len(self.authors_rank_order)
    if num_authors > self.top_size:
       num_authors= self.top_size
    for i in range (0,num_authors):
      (value,author)=self.authors_rank_order[i]
      self.top_authors[author]=value
    return
      
  def get_top_mentions(self):
    self.mentions_rank_order=sorted([(value,key) for (key,value) in self.dict_in.items()],reverse=True)
    num_mentions=len(self.mentions_rank_order)
    if num_mentions > self.top_size:
      num_mentions= self.top_size
    for i in range (0,num_mentions):
      (value,user)=self.mentions_rank_order[i]
      self.top_mentions[user]=value
    return  

    
  def get_links(self):
    self.links_rank_order=sorted([(value,key) for (key,value) in self.dict_links.items()],reverse=True)
    i=0
    for (value,user) in self.links_rank_order:
      self.dict_rank_links[user]=i
      self.dict_rank_links_index[i]=user
      i=i+1
    return

  def get_top_links(self):
    
    num_links=len(self.links_rank_order)
    if num_links > self.top_size:
      num_links= self.top_size
    for i in range (0,num_links):
      (value,user)=self.links_rank_order[i]
      self.top[user] = self.dict_links[user]
    return 

  def set_relation_nodes(self, author,text,list_relations,relation):
    num_mentions=  len (list_relations)
    row=self.dict_rank_links[author]
    for user in list_relations:
      col=self.dict_rank_links[user]
      self.most_mentions_matrix.store (row,col, 1)
      if (user in self.top) and (author in self.top):
        num_mentions=self.top_matrix.store (row,col,1)
    return
   
  def  get_format_gdf (self, group):
    if group =='top':
      mentions_matrix= self.top_matrix
      max_nodes= self.top_size
    else: 
      mentions_matrix=self.most_mentions_matrix
      max_nodes= len(self.dict_rank_links)
    print 'type: ',group,'nodes: ', max_nodes  
    f_out=  codecs.open(self.prefix+'_'+group+'_'+self.relation+'.gdf', 'w',encoding='utf-8') 
    print 'generating gdf file'
  #print nodes
    num_nodes=0
    log_followers=0
    log_following=0
    log_statuses=0
    # print nodes
    num_nodes=0
    f_out.write ('nodedef>name VARCHAR,label VARCHAR,Links VARCHAR,Links_in VARCHAR,links_out VARCHAR,followers VARCHAR,following VARCHAR,statuses VARCHAR,\n')
    links_order=sorted([(value,key) for (key,value) in self.dict_rank_links.items()])
    num_nodes=0
    for (value,user) in links_order:
      if num_nodes >= max_nodes:
        break
      connections_in= self.dict_in.getitem(user)
      connections_out= self.dict_out.getitem(user)
      connections= connections_in + connections_out
      if connections >0:
        if user in self.dict_authors:
          (author,followers,following,statuses)=self.dict_authors[user]
          if int(followers) >0:
            log_followers=int(math.log(float(followers),10))
          if int(following) >0:
            log_following=int(math.log(float(following),10))
          if int(statuses) >0:
            log_statuses=int(math.log(float(statuses),10))
        else:
          (author,followers,following,statuses)=(user,0,0,0)
        user_index= self.dict_rank_links[user]  
        num_nodes= num_nodes +1  
        if num_nodes % 100000 == 0:
          print '%s nodes generated' % (num_nodes) 
        #print ('node %s %s conections %s' % (num_nodes,user,connections))  
        f_out.write ('%s, %s, %.0f, %.0f, %.0f, %.0f, %.0f, %.0f\n' % (user_index, user, connections,connections_in,connections_out,log_followers,log_following,log_statuses))
  # print arcs 
    f_out.write ('edgedef>node1 VARCHAR,node2 VARCHAR, directed BOOLEAN, weight VARCHAR;\n')
    num_edges=0
    mentions_matrix_order=sorted([(key,value) for (key,value) in mentions_matrix.items()])
    for (key,value) in mentions_matrix_order:
      #print value,key
      (i,j) = key
      num_mentions= mentions_matrix.getitem(i,j)
      if num_mentions >0:
        num_edges= num_edges +1  
        if num_edges % 100000 == 0:
          print '%s nodes generated' % (num_edges)   
        f_out.write ('%s,%s,true,%.0f\n' % (i,j,num_mentions))
    f_out.close()
    return
                 
def get_number (item):
  number=0
  match=(re.search (r"\d+",item))
  if match:
    number = int(match.group(0))
  return number

def main():

 # init data
  #get parameters
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='This script generates a file in gdf format for visualization in gephi')
  parser.add_argument('file_in', type=str, help='file with tweets list')
  parser.add_argument('--top_size', type=str,default=100, help='top size')
  action = parser.add_mutually_exclusive_group(required=True)
  action.add_argument('--RT', action='store_true',help='RT relation')
  action.add_argument('--mention', action='store_true', help='mention relation')
  action.add_argument('--reply', action='store_true', help='reply relation')

  #obtego los argumentos
  args = parser.parse_args()
  file_in= args.file_in
  top_size=int(args.top_size)
  if args.RT:
    type_relation='RT'
  if args.mention:
    type_relation='mention'
  if args.reply:
    type_relation='reply'

  filename=re.search (r"([\.]*[\w/-]+)\.([\w]*)", file_in)
  print 'file name', file_in
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  name=filename.group(0)
  prefix=filename.group(1)
 
  try:  
    f_in = codecs.open(file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',file_in
    exit (1)
  print '------> Extracting relation %s\n' % type_relation
  relation= Relation(prefix,top_size,type_relation)
  num_line=0
  line_old=''
  for line in f_in:
    line=line_old+line
    if line_old != '':
      print 'Repaired tweet', line
    num_line +=1
    if num_line >1:
      if num_line % 10000 == 0:
        print num_line 
      line=line.strip('\r\n')
      data=line.split('\t')
      if len(data) > 9 :
        line_old=''
        author=data[2].lower()
        text=data[3].lower()
        followers=get_number(data[6])
        following=get_number(data[7])
        statuses=get_number(data[8])
        info_author= (author,followers,following,statuses)
        relation.set_author (author,info_author)
        list_relations= relation.get_relation (text,type_relation)
        if len(list_relations) > 0:
          relation.set_relation (author,text, list_relations,type_relation)
      else:
        line_old=line
        print 'truncated tweet',line
 #extract and print top 
 
  relation.get_top_authors () 
  relation.get_links()
  relation.get_top_links()
  relation.get_top_mentions()
  print '-----> second pass'
  #sencond pass
  f_in.seek(0)
  num_line=0
  line_old=''
  for line in f_in:
    line=line_old+line
    num_line +=1
    if num_line >1:
      if num_line % 10000 == 0:
        print num_line 
      line=line.strip('\r\n')
      data=line.split('\t') 
      if len(data) > 9 :
        line_old=''
        author=data[2].lower()
        text=data[3].lower()
        list_relations= relation.get_relation (text,type_relation)
        if len(list_relations) > 0:
          relation.set_relation_nodes (author,text, list_relations,type_relation)
      else:
        line_old=line
  print 'format gdf'
  relation.get_format_gdf ('top')
  relation.get_format_gdf ('all')
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye! '

 
