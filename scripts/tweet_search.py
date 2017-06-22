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
import tweepy
from datetime import datetime
import codecs
import argparse

class oauth_keys(object):
  def __init__(self,  app_keys_file,user_keys_file):
    self.matrix={}
    self.app_keys_file = app_keys_file
    self.user_keys_file = user_keys_file
    self.app_keys=[]
    self.user_keys=[]
    self.dict_ratelimit={}
    
    f = open(self.app_keys_file, 'rU')
    for line in f: 
      self.app_keys.append(line.strip('\n'))
    f.close()
    f = open(self.user_keys_file, 'rU')
    for line in f: 
      self.user_keys.append(line.strip('\n'))
    f.close()
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
      if remaining_hits <1:
        print 'waiting for 15 minutes ->' + str(datetime.now())
        time.sleep(wait)
      self.dict_ratelimit[(type_resource,method)]= remaining_hits
      print 'remaing hits',remaining_hits
    except:
      print 'excepction cheking ratelimit, waiting for 15 minutes ->' + str(datetime.now())
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

def tweet_search (user_keys,api,file_out,query):

  tweets_list=[]
  head=False
  try:
    f=codecs.open(file_out, 'ru',encoding='utf-8',errors='ignore') 
  except:
    head=True
  f=codecs.open(file_out, 'a',encoding='utf-8',errors='ignore') 
  print 'results in %s\n' % file_out
  f_log= open(file_out+'.log','a')
  f_log.write(('%s\t') % ( datetime.now()))
 
  recent_tweet=1000
  n_tweets=0
  first_tweet=True
  hay_tweets=True
  if head:
    f.write ('id tweet\tdate\tauthor\ttext\tapp\tid user\tfollowers\tfollowing\tstauses\tlocation\turls\tgeolocation\tname\tdescription\turl_media\ttype media\tquoted\n')
  while hay_tweets:
    oauth_keys.check_rate_limits (user_keys,api,'search','/search/tweets',900)
    try:
      if first_tweet:
        #print 'since_id', recent_tweet
        page = api.search(query, since_id=recent_tweet,include_entities=True,result_type='recent',count=100)  
        first_tweet=False
      else:
        #print 'max_id', recent_tweet-1
        page = api.search(query, max_id=recent_tweet-1,include_entities=True,result_type='recent',count=100) 
    except:
      f_log.write('error en tweepy\t') 
      break
    print 'collected',n_tweets
    if len(page) == 0:
      hay_tweets=False
      break
    for statuse in page:
      recent_tweet= statuse.id
      statuse_quoted_text=None
      geoloc=None
      url_expanded =None
      url_media=None
      type_media=None
      location=None
      description=None
      name=None
      profile_user= statuse.user
      try:
        if hasattr(statuse, 'quoted_status_id'):
          if statuse.coordinates != None:
            print statuse.quoted_status_id
            statuse_quoted=statuse.quoted_status
            statuse_quoted_text=statuse_quoted.text
            statuse_quoted_text=re.sub('[\r\n\t]+', ' ',statuse_quoted_text)
            print 'tweet nested',statuse_quoted_text
      except:
        pass
      try:
        if hasattr(statuse,'coordinates'):
          if statuse.coordinates != None:
            coordinates=statuse.coordinates
            print coordinates
            list_geoloc = coordinates['coordinates']
            geoloc= '%s, %s' % (list_geoloc[0],list_geoloc[1])
      except:
        pass
      try:
        if hasattr (statuse,'entities'):
          entities=statuse.entities
          urls=entities['urls']
          if len (urls) >0:
            url=urls[0]
            url_expanded= url['expanded_url']
      except:
        pass
      text=re.sub('[\r\n\t]+', ' ',statuse.text)
      try:
        location=re.sub('[\r\n\t]+', ' ',statuse.user.location,re.UNICODE)
      except:
        pass
      try:
        description=re.sub('[\r\n\t]+', ' ',profile_user['description'],re.UNICODE)
      except:
        pass 
      try:    
        name=re.sub('[\r\n\t]+', ' ',profile_user['name'],re.UNICODE)
      except:
        pass
      try:
        tweet= '%s\t%s\t@%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %  (statuse.id,statuse.created_at,profile_user.screen_name,text, statuse.source,profile_user.id, profile_user.followers_count,profile_user.friends_count,profile_user.statuses_count,location,url_expanded, geoloc,name,description, url_media,type_media,statuse_quoted_text)
        tweets_list.append(tweet)
        f.write(tweet) 
        n_tweets= n_tweets +1 
      except :
        f_log.write('Twitter Error\t')     
# save tweets
  print 'collected',n_tweets

# write log file
  f_log.write(('wrote %s tweets\t') % ( n_tweets))
  f_log.write(('recent tweet Id %s \n') % (recent_tweet))
  f_log.close()    
  return

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Examples usage Twitter API REST, search method')
  parser.add_argument('keys_app', type=str, help='file with app keys')
  parser.add_argument('keys_user', type=str, help='file with user keys')
  parser.add_argument('--query', type=str, help='query')
  parser.add_argument('--file_out', type=str,default='tweet_store.txt', help='name file out')
  
  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.keys_app
  user_keys_file= args.keys_user
  query= args.query
  file_out=args.file_out
  #print query,file_out
  #autenticación con oAuth     
  user_keys= oauth_keys(app_keys_file,user_keys_file)
  api= oauth_keys.get_access(user_keys)

  filename=re.search (r"[\.]*[\w/-]+\.[\w]*", file_out)
  if not filename:
    print "bad filename",file_out
    exit (1)
  tweet_search (user_keys,api,file_out,query)
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)

     

