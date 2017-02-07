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
import tweepy
import time
import datetime
import codecs
import argparse

class oauth_keys(object):
  def __init__(self,  app_keys_file,user_keys_file):
    self.matrix={}
    self.app_keys_file = app_keys_file
    self.user_keys_file = user_keys_file
    self.app_keys=[]
    self.user_keys=[]
    
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
 
def check_rate_limits (api,type_resource,method,wait):
 
   try:
     result = api.rate_limit_status(resources=type_resource)
     resources=result['resources']
     resource=resources[type_resource]
     rate_limit=resource[method]
     limit=int(rate_limit['limit'])
     remaining_hits=int(rate_limit['remaining'])
     print 'remaing hits',remaining_hits
     if remaining_hits <3: 
       print 'ratelimit, waiting for 15 minutes'
       time.sleep(wait)
   except:
       print 'ratelimit, waiting for 15 minutes'
       time.sleep(wait) 
   return 

def get_user(api,user,flag_id_user,f_log):
  error = False  
  profile_text = '%s\n' % (user)
  print 'Getting user profile ',user
  check_rate_limits (api,'users','/users/show/:id',900)
  try:
    if flag_id_user:
      profile=api.get_user( user_id=user)
    else:
      profile=api.get_user( screen_name=user)
  except:
     error=True
     print 'Error getting profile ',user
     f_log.write(('%s:  error en tweepy, method users_show: \n')  % (user))
      
  if not error: 
    f_log.write(('%s:  OK \n')  % (user))
    timestamp=time.gmtime()
    timestamp_tweet='%s-%s-%s %s:%s:%s' % (timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday,timestamp.tm_hour,timestamp.tm_min,timestamp.tm_sec)
    try:
      location=re.sub('[\r\n\t]+', ' ', profile.location)
    except:
      location=None
    try:
      description= re.sub('[\r\n\t]+', ' ', profile.description) 
    except:
      description=None
    try:
      name= re.sub('[\r\n\t]+', ' ', profile.name)
    except:
      name=None
    profile_text=(('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n') % (profile.id, profile.screen_name, profile.followers_count, profile.friends_count, profile.statuses_count,profile.listed_count, profile.created_at, name,profile.time_zone, location,profile.url, profile.profile_image_url,description, timestamp_tweet ))
  return profile_text

def get_followers(api,user,f_log):
  followers_list=[]
  print 'Getting user followers',user
  
  try:
    for page in tweepy.Cursor(api.followers_ids,screen_name=user).pages():
      check_rate_limits (api,'followers','/followers/ids',900)
      for followers_id in page:
        followers_list.append(followers_id)
  except:
    f_log.write(('%s, %s error en tweepy, method followers, user %s\n')  % (time.asctime(),TypeError(),user)) 
  print '%s followers' % (len(followers_list))
  return followers_list

def get_following(api,user,f_log):
  following_list=[]
  print 'Getting user following ',user

  try:
    for page in tweepy.Cursor(api.friends_ids,screen_name=user).pages():
      check_rate_limits (api,'friends','/friends/ids',900)
      for following_id in page:
        following_list.append(following_id)
  except:
    f_log.write(('%s, %s error en tweepy, method friends, user %s\n')  % (time.asctime(),TypeError(),user)) 
  print '%s following' % (len(following_list))
  return following_list

def get_tweets(api,user,flag_id_user,f_log):  
  tweets_list=[]
  error=False
  pages=0
  print 'Getting user tweets ', user
  intentos=0
  num_pages=0
  first_tweet=True
  hay_tweets=True
  recent_tweet=1000
  while  hay_tweets:
    check_rate_limits (api,'statuses','/statuses/user_timeline',900)
    try:
      if first_tweet:
        if flag_id_user:
          page =api.user_timeline (user_id=user,since_id=recent_tweet,include_rts=1,count=200,include_entities=1)
        else:
          page =api.user_timeline (screen_name=user,since_id=recent_tweet,include_rts=1,count=200,include_entities=1)
        first_tweet=False
      else:
         if flag_id_user:
           page =api.user_timeline (user_id=user,max_id=recent_tweet,include_rts=1,count=200,include_entities=1)
         else:
           page =api.user_timeline (screen_name=user,max_id=recent_tweet,include_rts=1,count=200,include_entities=1)
    except:
      f_log.write(('%s, %s error en tweepy, method tweets, user %s\n')  % (time.asctime(),TypeError(),user)) 
      break
    print '--> len page', len(page) 
    #page is a list of statuses
    num_pages +=1
    if len(page) ==1:
        hay_tweets=False
        break
    print "--> num pages", num_pages
    for statuse in page:
      print recent_tweet,statuse.id
      recent_tweet= statuse.id
      url_expanded =None
      geoloc=None
      location=None
      statuse_quoted_text= None
      try:
        if hasattr(statuse, 'quoted_status_id'):
          print statuse.quoted_status_id
          statuse_quoted=statuse.quoted_status
          statuse_quoted_text=statuse_quoted.text
          statuse_quoted_text=re.sub('[\r\n\t]+', ' ',statuse_quoted_text)
          print 'tweet nested',statuse_quoted_text
      except:
	    pass
      if hasattr(statuse,'coordinates'):
        if statuse.coordinates != None:
          coordinates=statuse.coordinates
          print coordinates
          list_geoloc = coordinates['coordinates']
          geoloc= '%s, %s' % (list_geoloc[0],list_geoloc[1])
      if hasattr (statuse,'entities'):
        entities=statuse.entities
        urls=entities['urls']
        if len (urls) >0:
          url=urls[0]
          url_expanded= url['expanded_url']
      text=re.sub('[\r\n\t]+', ' ',statuse.text)
      try:
        location=re.sub('[\r\n\t]+', ' ',statuse.user.location,re.UNICODE)
      except:
        pass
      try:
        tweet= '%s\t%s\t@%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %  (statuse.id,statuse.created_at,statuse.author.screen_name,text, statuse.source,statuse.user.id,statuse.user.followers_count,statuse.user.friends_count,statuse.user.statuses_count,location,url_expanded, geoloc, statuse.retweet_count,statuse.retweeted,statuse.in_reply_to_status_id_str,statuse.favorite_count,statuse_quoted_text)
        tweets_list.append(tweet)
      except:
        pass
  return tweets_list

  
def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Examples usage Twitter API REST')
  parser.add_argument('keys_app', type=str, help='file with app keys')
  parser.add_argument('keys_user', type=str, help='file with user keys')
  parser.add_argument('file_users', type=str, help='file with list users')
  parser.add_argument('--id_user', action='store_true', help='use id instead screen name')
  action = parser.add_mutually_exclusive_group(required=True)
  action.add_argument('--profile', action='store_true',help='get profiles')
  action.add_argument('--followers', action='store_true',help='get followers')
  action.add_argument('--following', action='store_true',help='get following')
  action.add_argument('--tweets', action='store_true', help='get tweets')

  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.keys_app
  user_keys_file= args.keys_user
  file_users= args.file_users
  flag_id_user= args.id_user
  flag_profile=args.profile
  flag_followers=args.followers
  flag_following=args.following
  flag_tweets = args.tweets
  
  #obtengo el nombre y la extensión del ficheros con la lita de los usuarios
  filename=re.search (r"([\.]*[\w/-]+)\.([\w]+)",file_users)
  if not filename:
    print "bad filename",file_users, ' Must be an extension'
    exit (1)
  prefix=filename.group(1)
  try:
    f_users_group_file= open (file_users,'r')
  except:
    exit (1)   
  
  #autenticación con oAuth     
  user_keys= oauth_keys(app_keys_file,user_keys_file)
  api= oauth_keys.get_access(user_keys)

  f_log= open (prefix+'_log.txt','w')
  # acciones
  if flag_profile:
    f_out=  codecs.open(prefix+'_profiles.txt', 'w',encoding='utf-8', errors='ignore')
    print "--> Results in %s_profiles.txt\n" % prefix   
    f_out.write ('id user\tscreen_name\tfollowers\tfollowing\tstatuses\tlists\tsine\tname\ttime zone\tlocation\tweb\tavatar\tbio\ttimestamp\n')
    for line in f_users_group_file:
      user= line.strip("\n")
      profile= get_user (api, user,flag_id_user,f_log) 
      f_out.write (profile)
    f_out.close()
  if flag_followers:
    for line in f_users_group_file:
      user= line.strip("\n")
      profile= get_user (api, user,flag_id_user,f_log)
      name_file_out= '%s_%s_followers_profiles.txt' % (prefix,user.strip('@')) 
      f_out=  codecs.open(name_file_out, 'w',encoding='utf-8', errors='ignore')
      print "-->Results in %s\n" % (name_file_out)
      f_out.write ('id user\tscreen_name\tfollowers\tfollowing\tstatuses\tlists\tsine\tname\ttime zone\tlocation\tweb\tavatar\tbio\ttimestamp\n') 
      list_followers = get_followers (api,user,f_log)
      for follower in list_followers:
        profile= get_user (api,follower,True,f_log)
        f_out.write (profile)
      f_out.close()
  if flag_following:
    for line in f_users_group_file:
      user= line.strip("\n")
      profile= get_user (api, user,flag_id_user,f_log)
      name_file_out= '%s_%s_following_profiles.txt' % (prefix,user.strip('@')) 
      f_out=  codecs.open(name_file_out, 'w',encoding='utf-8', errors='ignore')
      print "-->Results in %s\n" % (name_file_out) 
      f_out.write ('id user\tscreen_name\tfollowers\tfollowing\tstatuses\tlists\tsine\tname\ttime zone\tlocation\tweb\tavatar\tbio\ttimestamp\n')
      list_following = get_following (api,user,f_log)
      for following in list_following:
        profile= get_user (api,following,True,f_log)
        f_out.write (profile)
      f_out.close()
  if flag_tweets:
    f_out=  codecs.open(prefix+'_tweets.txt','w',encoding='utf-8')
    print "-->Results in %s_tweets.txt\n" % prefix
    f_out.write ('id tweet\tdate\tauthor\ttext\tapp\tid user\tfollowers\tfollowing\tstauses\tlocation\turls\tgeolocation\tRT count\tRetweed\tin reply\tfavorite count\tquoted\n')
    for line in f_users_group_file:
      user= line.strip('\n')
      tweets= get_tweets (api,user,flag_id_user,f_log) 
      for tweet in tweets:
        f_out.write (tweet)
    f_out.close()
  f_log.close()
  f_users_group_file.close()
  exit(0)

if __name__ == '__main__':
  main()

