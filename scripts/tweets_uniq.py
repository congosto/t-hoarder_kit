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

def main():

  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino datos del script
  dict_id= {}
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Getting files')
  parser.add_argument('file_in', type=str, help='File with the tweets')
  parser.add_argument('file_out', type=str,help='File with result')
  #get arguments
  args = parser.parse_args()
  file_in= args.file_in
  file_out= args.file_out
  print file_in, file_out
  print 'file in name', file_in
  filename=re.search (r"([\w-]+)\.([\w]*)", file_in)
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  prefix = filename.group(1)
  print 'file out name', file_out
  filename=re.search (r"([\w-]+)\.([\w]*)", file_out)
  if not filename:
    print "bad filename",file_out, ' Must be an extension'
    exit (1)
  # get start time and end time 
  try:  
    f_in= codecs.open(file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',file_in
    exit (1)
    
  f_out = codecs.open(file_out, 'w',encoding='utf-8')  
  f_log = codecs.open(prefix+'.log', 'w',encoding='utf-8')
  num_select_tweets=0
  is_head = True
  num_tweets=0
  for tweet in f_in:
    try:
      num_tweets=num_tweets +1 
      if num_tweets % 10000 == 0:
          print num_tweets  
      if is_head:
        f_out.write(tweet)
        is_head = False
      else:
        tweet_in= re.search(r'(\d+)',tweet)
        if tweet_in:
          id_tweet=tweet_in.group(1)
          if id_tweet not in dict_id:
            f_out.write(tweet)
            dict_id[id_tweet]=1
          else:
            f_log.write(tweet)
        else:
          print 'not match',tweet
    except:
      print 'not match'
      pass
  f_out.close()
  f_in.close()
  f_log.close()
  exit(0)

if __name__ == '__main__':
  main()

