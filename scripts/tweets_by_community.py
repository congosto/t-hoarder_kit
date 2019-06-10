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

def get_tweet (line):
   line= line.strip('\n')
   data=line.split('\t')
   #if True:
   try:
     i=len(data)-1
     community=data[i]
     return community
   #else:
   except:
     print ' tweet not match', line
     return None

def get_community (file):
    list_community =[]
    f = codecs.open(file, 'rU',encoding='utf-8')
    for line in f:
       line= line.strip('\n\r')
       data=line.split('\t')
       num_community=data[0]
       list_community.append (num_community)
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
  #obtego los argumentos
  args = parser.parse_args()
  file_in= args.file_in
  dir_out=args.dir_out
  file_community=args.community
  list_communities=[]
  file_base=os.path.basename(file_in)
  (prefix,text)=os.path.splitext(file_base)
  file_base=os.path.basename(file_community)
  (prefix_comunity,text)=os.path.splitext(file_base)
  try:
    f_in = codecs.open(file_in, 'rU',encoding='utf-8')
    print 'open as unicode'
  except:
    print 'Can not open file',file_in
    exit (1)
  head=True
  n_tweets=0
  list_community=get_community (file_community)
  f_out= open(dir_out+'/'+prefix+'_'+prefix_comunity+'.txt','w')
  f_log= open(dir_out+'/'+prefix+'.log','w')
  print list_community
  for line in f_in:
    index=line.find('\t')
    line=line[index+1:]
    if (n_tweets % 10000) == 0:
      print n_tweets
    n_tweets +=1
    if head:
      head=False
    else:
     community = get_tweet (line)
     if community in list_community:
       f_out.write(line)
  f_out.close ()
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
