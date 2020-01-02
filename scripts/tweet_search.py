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
import csv
import unicodecsv as csv
import logging

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
      print 'Error in oauth authentication, user key ', user_keys_file
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
        print 'remaining hits',remaining_hits
    except:
      print 'exception checking ratelimit, waiting for 15 minutes ->' + str(datetime.now())
      print 'If the same error occurred after 15 minutes, please abort the command and check the app-user access keys'
      time.sleep(wait)
    return
 
  def check_rate_limits (self,api,type_resource,method,wait):
    if (type_resource,method) not in self.dict_ratelimit:
      self.get_rate_limits (api,type_resource,method,wait)
    else:
      self.dict_ratelimit[(type_resource,method)]-= 1
      print 'remaining hits',self.dict_ratelimit[(type_resource,method)]
      if self.dict_ratelimit[(type_resource,method)] <1 :
        self.get_rate_limits (api,type_resource,method,wait)
    return 

def tweet_search (user_keys,api,file_out,query,format):
  head=False
  try:
    f=codecs.open(file_out, 'ru',encoding='utf-8',errors='ignore') 
  except:
    head=True
  f=codecs.open(file_out, 'a',encoding='utf-8',errors='ignore') 
  print 'results in %s\n' % file_out
  f_log= open(file_out+'.log','a')
  f_log.write(('%s\t') % ( datetime.now()))
  n_tweets=0
  recent_tweet=0
  first_tweet=True
  f_log.write(('%s\t') % ('First time\t'))
  if format == 'text':
    print 'generate file txt'
  if format == 'csv':
    print 'generate file csv'
    writer = csv.writer(f,delimiter=';')
  if head:
    if format == 'text':
      f.write ('id tweet\tdate\tauthor\ttext\tapp\tid user\tfollowers\tfollowing\tstauses\tlocation\turls\tgeolocation\tname\tdescription\turl_media\ttype media\tquoted\trelation\treplied_id\tuser replied\tretweeted_id\tuser retweeted\tquoted_id\tuser quoted\tfirst HT\tlang\tcreated_at\tverified\tavatar\tlink\n')
    if format == 'csv':
      title= ['id tweet','date','author','text','app','id user','followers','following','stauses','location','urls','geolocation','name','description','url_media','type media','quoted','relation','replied_id','user replied','retweeted_id','user retweeted','quoted_id','user quoted','first HT','lang','created at','verified','avatar','link']
      writer.writerow(title)
  while True:
    try:
      oauth_keys.check_rate_limits (user_keys,api,'search','/search/tweets',900)
      error=False
      if first_tweet:
        #print 'since_id', recent_tweet
        page = api.search(query, since_id=recent_tweet,include_entities=True,result_type='recent',count=100,tweet_mode='extended')  # SearchResults containing list of statuses plus meta data
        first_tweet=False
      else:
        #print 'max_id', recent_tweet-1
        page = api.search(query, max_id=recent_tweet-1,include_entities=True,result_type='recent',count=100,tweet_mode='extended')  # SearchResults containing list of statuses plus meta data
    except KeyboardInterrupt:
      print '\nGoodbye!'
      exit(0)
    except tweepy.TweepError as e:
      text_error = '---------------->Tweepy error tweet at %s %s\n' % (time.asctime(),e)
      f_log.write (text_error)
      error=True
    if len(page) == 0:
      break
    if not error:
      print 'collected',n_tweets
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
        relation=None
        quoted_id=None
        replied_id=None
        retweeted_id=None
        user_replied=None
        user_quoted=None
        user_retweeted=None
        first_HT=None
#get interactions Ids
        try:
          id_tweet=statuse.id_str
          if statuse.in_reply_to_status_id_str != None:
            relation='reply'
            replied_id= statuse.in_reply_to_status_id_str
            user_replied='@'+statuse.in_reply_to_screen_name
          if hasattr(statuse, 'quoted_status'):
            relation='quote'
            quoted_id=statuse.quoted_status_id_str
            user_quoted='@'+statuse.quoted_status['user']['screen_name']
          elif hasattr(statuse,'retweeted_status'):
            relation='RT'
            retweeted_id=statuse.retweeted_status.id_str
            user_retweeted='@'+statuse.retweeted_status.user.screen_name
            if hasattr(statuse.retweeted_status,'quoted_status'):
              quoted_id=statuse.retweeted_status.quoted_status['id_str']
              user_quoted='@'+statuse.retweeted_status.quoted_status['user']['screen_name']
        except:
          text_error = '---------------->Warning (tweet not discarded): bad interactions ids, id tweet %s at %s \n' % (id_tweet,time.asctime())
          f_log.write (text_error)
#get quote
        if hasattr(statuse, 'quoted_status'):
          try:
            statuse_quoted_text=statuse.quoted_status['full_text']
            statuse_quoted_text=re.sub('[\r\n\t]+', ' ',statuse_quoted_text)
          except:
            text_error = '---------------->Warning (tweet not discarded): bad quoted, id tweet %s at %s\n' % (id_tweet,time.asctime())
            print text_error
            f_log.write (text_error)
        elif hasattr(statuse, 'retweeted_status'):
          try:
            if hasattr(statuse.retweeted_status,'quoted_status'):
              statuse_quoted_text=statuse.retweeted_status.quoted_status['full_text']
              statuse_quoted_text=re.sub('[\r\n\t]+', ' ',statuse_quoted_text)
          except:
            print text_error
            text_error = '---------------->Warning (tweet not discarded): bad quoted into a RT, id tweet %s at %s\n' % (id_tweet,time.asctime())
            f_log.write (text_error)
#get geolocation
        if hasattr(statuse,'coordinates'):
          coordinates=statuse.coordinates
          if coordinates != None:
            try:
              if 'coordinates' in coordinates:
                list_geoloc = coordinates['coordinates']
                print list_geoloc
                geoloc= '%s, %s' % (list_geoloc[0],list_geoloc[1])
            except:
              text_error = '---------------->Warning (tweet not discarded): bad coordinates, id tweet %s at %s\n' % (id_tweet,time.asctime())
              f_log.write (text_error)
#get entities
        if hasattr (statuse,'entities'):
          entities=statuse.entities
        if  hasattr (statuse,'retweeted_status'):
          if hasattr (statuse.retweeted_status,'entities'):
            entities=statuse.retweeted_status.entities
        if entities != None:
          try:
            urls=entities['urls']
            if len (urls) >0:
              url_expanded= urls[0]['expanded_url']
          except:
            text_error = '---------------->Warning (tweet not discarded):  bad entity urls, id tweet %s at %s\n' % (id_tweet,time.asctime())
            self.f_log.write (text_error)
          try:
            if 'media' in entities:
              list_media=entities['media']
              if len (list_media) >0:
                url_media= list_media[0]['media_url']
                type_media=list_media[0]['type']
          except:
            text_error = '---------------->Warning (tweet not discarded): bad entity Media, id tweet %s at %s\n' % (id_tweet,time.asctime())
            f_log.write (text_error)
          try:
            if 'hashtags' in entities:
              HTs=entities['hashtags']
              if len (HTs) >0:
                first_HT=HTs[0]['text']
          except:
            text_error = '---------------->Warning (tweet not discarded): bad entity HT, id tweet %s at %s\n' % (id_tweet,time.asctime())
            f_log.write (text_error)
#get text
        if hasattr (statuse,'full_text'):
          try:
            text=re.sub('[\r\n\t]+', ' ',statuse.full_text)
          except:
            text_error = '---------------->Warning (tweet not discarded): bad tweet text,  at %s id tweet %s \n' % (time.asctime(),id_tweet)
            f_log.write (text_error)
        if hasattr(statuse,'retweeted_status'):
          if hasattr (statuse.retweeted_status,'full_text'):
            try:
              RT_expand=re.sub('[\r\n\t]+', ' ',statuse.retweeted_status.full_text)
              RT=re.match(r'(^RT @\w+: )',text)
              if RT:
               text= RT.group(1) + RT_expand
            except:
              text_error = '---------------->Warning (tweet not discarded): bad tweet text into a RT,  at %s id tweet %s \n' % (time.asctime(),id_tweet)
              f_log.write (text_error)
        try:
            location=re.sub('[\r\n\t]+', ' ',statuse.user.location,re.UNICODE)
        except:
          pass
        try:
          description=re.sub('[\r\n\t]+', ' ',statuse.user.description,re.UNICODE)
        except:
          pass 
        try:    
          name=re.sub('[\r\n\t]+', ' ',statuse.user.name,re.UNICODE)
        except:
          pass
        try:
          link_tweet= 'https://twitter.com/%s/status/%s' % (statuse.user.screen_name,statuse.id)
          if format == 'text':
            tweet= '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %  (statuse.id,
                  statuse.created_at,
                  '@'+statuse.user.screen_name,
                  text,
                  statuse.source,
                  statuse.user.id,
                  statuse.user.followers_count,
                  statuse.user.friends_count,
                  statuse.user.statuses_count,
                  location,
                  url_expanded,
                  geoloc,
                  name,
                  description,
                  url_media,
                  type_media,
                  statuse_quoted_text,
                  relation,
                  replied_id,
                  user_replied,
                  retweeted_id,
                  user_retweeted,
                  quoted_id,
                  user_quoted,
                  first_HT,
                  statuse.lang,
                  statuse.user.created_at,
                  statuse.user.verified,
                  statuse.user.profile_image_url_https,
                  link_tweet)
            f.write(tweet)
          if format =='csv':
            row=[]
            row.append(statuse.id)
            row.append(statuse.created_at)
            row.append('@'+statuse.user.screen_name)
            row.append(text)
            row.append(statuse.source)
            row.append(statuse.user.id)
            row.append(statuse.user.followers_count)
            row.append(statuse.user.friends_count)
            row.append(statuse.user.statuses_count)
            row.append(location)
            row.append(url_expanded)
            row.append(geoloc)
            row.append(name)
            row.append(description)
            row.append(url_media)
            row.append(type_media)
            row.append(statuse_quoted_text)
            row.append(relation)
            row.append(replied_id)
            row.append(user_replied)
            row.append(retweeted_id)
            row.append(user_retweeted)
            row.append(quoted_id)
            row.append(user_quoted)
            row.append(first_HT)
            row.append(statuse.lang)
            row.append(statuse.user.created_at)
            row.append(statuse.user.verified)
            row.append(statuse.user.profile_image_url_https)
            row.append(link_tweet)
            writer.writerow(row)
          n_tweets= n_tweets +1
        except :
          text_error = '---------------->bad format,  at %s id tweet %s \n' % (time.asctime(),id_tweet)
          f_log.write (text_error)
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
  parser.add_argument('--format', type=str,default='text', help='name file out')
  
  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.keys_app
  user_keys_file= args.keys_user
  query= args.query
  file_out=args.file_out
  format=args.format
  #print query,file_out
  #autenticación con oAuth     
  user_keys= oauth_keys(app_keys_file,user_keys_file)
  api= oauth_keys.get_access(user_keys)

  filename=re.search (r"[\.]*[\w/-]+\.[\w]*", file_out)
  if not filename:
    print "bad filename",file_out
    exit (1)
  tweet_search (user_keys,api,file_out,query,format)
  exit(0)

if __name__ == '__main__':
  try:
    logging.basicConfig()
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
