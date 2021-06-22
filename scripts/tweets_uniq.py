#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# author: M. Luz Congosto.
# Creative commons 3.0 spain
# http://creativecommons.org/licenses/by-nc/3.0/es/

import os
import re
import sys
import time
import datetime
import codecs

"""
This script extracts remove tweets repeted.


 usage: tweets_uniq.o file_in   file_out  
 
"""
       
  
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# main
# author M.L. Congosto
# 21-may-2015
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
# intit data
  dict_id={} 
  args = sys.argv[1:]

  if len (args) < 2:
    print 'tweets_uniq.o file_in   file_out'
    exit (1)
  file_in=args.pop(0)
  filename=re.search (r"([\w-]+)\.([\w]*)", file_in)
  print 'file name', file_in
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  name=filename.group(0)
  prefix=filename.group(1)
  file_out=args.pop(0)
  filename=re.search (r"([\w-]+)\.([\w]*)", file_in)
  print 'file name', file_out
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  name=filename.group(0)
  prefix=filename.group(1)
   
  # get start time and end time 
  try:  
    f_in= codecs.open(file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',file_in
    exit (1)
    
  f_out = codecs.open(file_out, 'w',encoding='utf-8')  
  f_log = codecs.open(prefix+'.log', 'w',encoding='utf-8')
  num_select_tweets=0
  num_tweets=0
  while True:
    if True:
    #try:
      tweet=f_in.readline()
      if tweet =='':
        break
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
    else:
    #except:
      print 'not match'
      pass
  f_out.close()
  f_in.close()
  f_log.close()
  exit(0)

if __name__ == '__main__':
  main()

