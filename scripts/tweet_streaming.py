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
import tweepy
from getpass import getpass
from textwrap import TextWrapper
import codecs
import argparse
from tweepy.utils import import_simplejson
json = import_simplejson()
from tweepy.utils import parse_datetime, parse_html_value, parse_a_href

class oauth_keys(object):
  def __init__(self,  app_keys_file,user_keys_file):
    self.matrix={}
    self.app_keys_file = app_keys_file
    self.user_keys_file = user_keys_file
    app_keys=[]
    user_keys=[]
    f = open(self.app_keys_file, 'rU')
    for line in f: 
      app_keys.append(line.strip('\n'))
#    print app_keys
    f.close()
    f = open( self.user_keys_file, 'rU')
    for line in f: 
      user_keys.append(line.strip('\n'))
    f.close()
    try: 
      self.auth = tweepy.OAuthHandler(app_keys[0],app_keys[1])
      self.auth.secure = True
      self.auth.set_access_token(user_keys[0], user_keys[1])
    except:
      print 'Error in oauth autentication, user key ', user_keys_file_num
      exit(83)
    return
  def get_auth(self):
    return self.auth
    
#based on joshthecoder example http://github.com/joshthecoder/tweepy-examples/blob/master/streamwatcher.py
class StreamWatcherListener(tweepy.StreamListener):

  def __init__(self,dir_dest,prefix,ext,auth):
    self.start_time= time.time()
    self.last_time= self.start_time
    self.api = tweepy.API(auth)
    self.status='remaining'       
    head=False
    file_out='%s/%s.%s' % (dir_dest,prefix,ext)
    file_log='%s/%s.log' % (dir_dest,prefix)
    try:
      self.f_out= codecs.open(file_out, 'ru',encoding='utf-8')
    except:
     head=True
    self.f_out= codecs.open(file_out, 'a',encoding='utf-8')
    self.f_log= codecs.open(file_log, 'a',encoding='utf-8')
    self.f_log.write (('====================> file %s  %s at %s\n') % ( file_out,self.status, datetime.datetime.now()))
    self.f_log.flush()
    if head:
      self.f_out.write ('id tweet\tdate\tauthor\ttext\tapp\tid user\tfollowers\tfollowing\tstauses\tlocation\turls\tgeolocation\tname\tdescription\turl_media\ttype media\tquoted\trelation\treplied_id\tuser replied\tretweeted_id\tuser retweeted\tquoted_id\tuser quoted\tfirst HT\tlang\tlink\n')

  def on_data(self, data):
    statuse = json.loads(data)
    if 'delete' in statuse:
      return True # keep stream alive
    if 'id' in statuse:
      statuse_quoted_text=None
      geoloc=None
      url_expanded =None
      url_media=None
      type_media=None
      text=None
      location=None
      description=None
      name=None
      date = parse_datetime(statuse['created_at'])
      app = parse_html_value(statuse['source'])
      entities=None
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
        id_tweet=statuse['id_str']
        if statuse['in_reply_to_status_id_str'] != None:
          relation='reply'
          replied_id= statuse['in_reply_to_status_id_str']
          user_replied=statuse['in_reply_to_screen_name']
        if 'quoted_status' in statuse:
          relation='quote'
          quoted_id=statuse['quoted_status_id_str']
          user_quoted=statuse['quoted_status']['user']['screen_name']
        elif 'retweeted_status' in statuse:
          relation='RT'
          retweeted_id=statuse['retweeted_status']['id_str']
          user_retweeted=statuse['retweeted_status']['user']['screen_name']
          if 'quoted_status' in statuse['retweeted_status']:
            quoted_id=statuse['retweeted_status']['quoted_status']['id_str']
            user_quoted=statuse['retweeted_status']['quoted_status']['user']['screen_name']
      except:
        text_error = '---------------->bad interactions ids, id tweet %s at %s\n' % (id_tweet,time.asctime())
        self.f_log.write (text_error)
#get geolocation
      if 'coordinates' in statuse:
        coordinates=statuse['coordinates']
        if coordinates != None:
          try:
            if 'coordinates' in coordinates:
              list_geoloc = coordinates['coordinates']
              print list_geoloc
              geoloc= '%s, %s' % (list_geoloc[0],list_geoloc[1])
          except:
            text_error = '---------------->bad coordinates, id tweet %s at %s\n' % (id_tweet,datetime.datetime.now())
            self.f_log.write (text_error)
#get entities
      if 'entities' in statuse:
        entities=statuse['entities']
      if 'extended_tweet' in statuse:
        entities=statuse['extended_tweet']['entities']
      if 'retweeted_status' in statuse:
        if 'entities' in statuse['retweeted_status']:
          entities=statuse['retweeted_status']['entities']
        if 'extended_tweet' in statuse['retweeted_status']:
          entities=statuse['retweeted_status']['extended_tweet']['entities']
      if entities != None:
        try:
          urls=entities['urls']
          if len (urls) >0:
            url_expanded= urls[0]['expanded_url']
        except:
          text_error = '---------------->bad enttity urls, id tweet %s at %s\n' % (id_tweet,datetime.datetime.now())
          self.f_log.write (text_error)
        try:
          if 'media' in entities:
            list_media=entities['media']
            if len (list_media) >0:
              url_media= list_media[0]['media_url']
              type_media=list_media[0]['type']
        except:
          text_error = '---------------->bad entity media, at %s id tweet %s \n' % (datetime.datetime.now(),id_tweet)
          self.f_log.write (text_error)
        try:
          if 'hashtags' in entities:
            HTs=entities['hashtags']
            if len (HTs) >0:
              first_HT=HTs[0]['text']
        except:
          text_error = '---------------->bad entity HT, id tweet %s at %s\n' % (id_tweet,time.asctime())
          self.f_log.write (text_error)
#get text
      try:
        if 'text' in statuse:
          text=re.sub('[\r\n\t]+', ' ',statuse['text'])
        if 'extended_tweet' in statuse:
          text=re.sub('[\r\n\t]+', ' ',statuse['extended_tweet']['full_text'])
        if 'retweeted_status' in statuse:
          statuse_RT= statuse['retweeted_status']
          if 'text' in statuse_RT:
            RT_expand=re.sub('[\r\n\t]+', ' ',statuse_RT['text'])
          if 'extended_tweet' in statuse_RT:
            extended_RT= statuse_RT['extended_tweet']
            RT_expand=re.sub('[\r\n\t]+', ' ',extended_RT['full_text'])
          RT=re.match(r'(^RT @\w+: )',text)
          if RT:
            text= RT.group(1) + RT_expand
      except:
          text_error = '---------------->bad tweet text,  at %s id tweet %s \n' % (datetime.datetime.now(),id_tweet)
          self.f_log.write (text_error)
#get quoted if exist
      try:
        if 'quoted_status' in statuse:
          if 'text' in statuse['quoted_status']:
            statuse_quoted_text=statuse['quoted_status']['text']
          if 'extended_tweet' in statuse['quoted_status']:
            statuse_quoted_text=statuse['quoted_status']['extended_tweet']['full_text']
          statuse_quoted_text=re.sub('[\r\n\t]+', ' ',statuse_quoted_text)
        elif 'retweeted_status' in statuse:
          if 'quoted_status' in statuse['retweeted_status']:
            if 'text' in statuse['retweeted_status']['quoted_status']:
              statuse_quoted_text=statuse['retweeted_status']['quoted_status']['text']
            if 'extended_tweet' in statuse['retweeted_status']['quoted_status']:
              statuse_quoted_text=statuse['retweeted_status']['quoted_status']['extended_tweet']['full_text']
            statuse_quoted_text=re.sub('[\r\n\t]+', ' ',statuse_quoted_text)
      except:
        text_error = '---------------->bad quoted,  at %s id tweet %s \n' % (datetime.datetime.now(),id_tweet)
        self.f_log.write (text_error)
#get user profile
      if 'user' in statuse:
        try:
          if 'location' in statuse['user']:
            if statuse['user']['location'] != None:
              location=re.sub('[\r\n\t]+', ' ',statuse['user']['location'],re.UNICODE)
        except:
          text_error = '---------------->bad user location:%s ,  at %s id tweet %s \n' % (datetime.datetime.now(),statuse['user']['location'],id_tweet)
          self.f_log.write (text_error)
        try:
          if 'description' in statuse['user']:
            if statuse['user']['description'] != None:
              description=re.sub('[\r\n\t]+', ' ',statuse['user']['description'],re.UNICODE)
        except:
          text_error = '---------------->bad user description,  at %s id tweet %s \n' % (datetime.datetime.now(),id_tweet)
          self.f_log.write (text_error)
        try:
          if 'name' in statuse['user']:
            if statuse['user']['name'] != None:
              name=re.sub('[\r\n\t]+', ' ',statuse['user']['name'],re.UNICODE)
        except:
          text_error = '---------------->bad user name,  at %s id tweet %s \n' % (datetime.datetime.now(),id_tweet)
          self.f_log.write (text_error) 
      try:
        link_tweet= 'https://twitter.com/%s/status/%s' % (statuse['user']['screen_name'],id_tweet)
        tweet='%s\t%s\t@%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %  (id_tweet,
                date,
                statuse['user']['screen_name'],
                text,
                app,
                statuse['user']['id'],
                statuse['user']['followers_count'],
                statuse['user']['friends_count'],
                statuse['user']['statuses_count'],
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
                statuse['lang'],
                link_tweet)
        self.f_out.write(tweet) 
        print '---->collected tweet', id_tweet
      except:
        text_error = '---------------> format error  at %s, id-tweet %s\n' % ( datetime.datetime.now(),id_tweet)
        self.f_log.write (text_error)
        pass
    else:
      text_error = '---------------> message no expected  %s,  %s\n' % ( datetime.datetime.now(),data)
      self.f_log.write (text_error)
    return True # keep stream alive

  def on_error(self, status_code):
    #print 'paso por on_error\n'
    text_error = '---------------->An error has occured! Status code = %s at %s\n' % (status_code,datetime.datetime.now())
    self.f_log.write (text_error)
    print text_error
    return True # keep stream alive

  def on_exception(self,exception):
   text_error = '---------------->An excepcion has occured!  = %s at %s\n' % (exception,datetime.datetime.now())
   self.f_log.write (text_error)
   print text_error
   return True # keep stream alive
 
  def on_timeout(self):
    #print 'paso por on_timeout\n'
    text_error = 'Snoozing Zzzzzz at %s\n' % ( datetime.datetime.now())
    self.f_log.write (text_error)
    print text_error
    return False #restart streaming

def get_list (file_list):
  try:
    f_list= open(file_list,'rU')
  except:
    print "file doesn't exist:", file_list
    exit(1)
  list_plana= f_list.read()
  list_datos= list_plana[:-1].split (',')
  return list_datos

def main():
  follow_list=None
  track_list=None
  locations_list=None
  locations_list_int=[]
  
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='get tweets from Streaming API ')
  parser.add_argument('app_keys', type=str, help='file with keys app')
  parser.add_argument('user_keys', type=str,help='file with user token access')
  parser.add_argument('dir_out', type=str, help='Dir data output')
  parser.add_argument('file_dest', type=str, help='file to store raw tweets')
  parser.add_argument('--users', type=str, default='', help='get tweets for id_tweets')
  parser.add_argument('--words', type=str, default='', help='get tweets for keywords')
  parser.add_argument('--locations', type=str, default='', help='get tweets for location')
  
  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.app_keys
  user_keys_file= args.user_keys
  dir_dest= args.dir_out
  file_out= args.file_dest
  file_users=args.users
  file_words=args.words
  file_location = args.locations
  if file_users != '':
    follow_list=get_list (file_users)
  if file_words != '':
    track_list=get_list (file_words)
  if file_location != '':
     locations_list=get_list (file_location)
     for location in locations_list:
        locations_list_int.append (float(location))
  filename=re.search (r"([\w-]+)\.([\w]+)*", file_out)
  if not filename:
    print "%s bad filename, it must have an extension xxxx.xxx",file_out
    exit (1)
  prefix= filename.group(1)
  ext= filename.group(2)
  print '-->File output: ', file_out
  oauth=oauth_keys(app_keys_file,user_keys_file)
  auth=oauth.get_auth()
  print "autenticated"
  exit=False
  while not exit: # Making permanent streaming with exception handling 
    try:
       stream = tweepy.Stream(auth, StreamWatcherListener(dir_dest,prefix,ext,auth))
       stream.filter(follow_list, track_list,False,locations_list_int)
    except KeyboardInterrupt:
       print '\nGoodbye! '
       exit = True
    except tweepy.TweepError as err:
       print(err)
       print "Restarting Stream.... " 
       
       time.sleep(5)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye! '
