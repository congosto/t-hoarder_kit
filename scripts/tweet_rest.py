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
from datetime import datetime
import codecs
import math
import argparse

class oauth_keys(object):
  def __init__(self,  app_keys_file,user_keys_file):
    self.matrix={}
    self.app_keys_file = app_keys_file
    self.user_keys_file = user_keys_file
    self.app_keys=[]
    self.user_keys=[]
    try:
      f = open(self.app_keys_file, 'rU')
      for line in f: 
        self.app_keys.append(line.strip('\n'))
      f.close()
    except:
      print 'File does not exist %s' % self.app_keys_file
      exit (1)
    try:
      f = open(self.user_keys_file, 'rU')
      for line in f: 
        self.user_keys.append(line.strip('\n'))
      f.close()
    except:
      print 'File does not exist %s' % self.user_keys_file
      exit (1)
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
  result = api.rate_limit_status(resources=type_resource)
  resources=result['resources']
  resource=resources[type_resource]
  rate_limit=resource[method]
  limit=int(rate_limit['limit'])
  remaining_hits=int(rate_limit['remaining'])
  print 'remaing hits',remaining_hits
  if remaining_hits <1 :
    print 'ratelimit, waiting for 15 minutes ->' + str(datetime.now())
    time.sleep(wait)
  return 

class Format_gdf(object):
  def __init__(self,  prefix):
    self.f_gdf= open (prefix+'.gdf','w')
    print "-->Result in %s.gdf" % prefix
    self.nodes='nodedef>name VARCHAR,label VARCHAR,net VARCHAR,relation VARCHAR, num_followers VARCHAR, num_following VARCHAR, num_list VARCHAR, num_statuses VARCHAR, user_TZ VARCHAR \n'
    self.arcs='edgedef>node1 VARCHAR,node2 VARCHAR\n'
    return
 
  def put_node(self,id_node,user_name,net,relation,num_followers,num_following,num_list,num_statuses,user_TZ):
    log_followers=0
    log_following=0
    log_statuses=0
    log_list=0
    if int(num_followers) >0:
      log_followers=int(math.log(float(num_followers),10))
    if int(num_following) >0:
      log_following=int(math.log(float(num_following),10))
    if int(num_statuses) >0:
      log_statuses=int(math.log(float(num_statuses),10))
    if int(num_list) >0:
      log_list=int(math.log(float(num_list),10))
    self.nodes = self.nodes + ('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (id_node,user_name,net,relation,log_followers,log_following,log_list,log_statuses,user_TZ))
    return
     
  def put_arc(self,orig,dest):
    self.arcs = self.arcs + ('%s,%s\n' % (orig,dest))
    return
    
  def print_graph(self):
    self.f_gdf.write (self.nodes)
    self.f_gdf.write (self.arcs)
    self.f_gdf.close ()
    return

def how_long_it_takes (dict_user_attrib,flag_fast):
  dict_top={}
  num_requests=0
  num_users=len(dict_user_attrib)
  for key in dict_user_attrib:
    (i,user_name,net,relation,num_followers,num_following,num_list,num_statuses,user_TZ)=dict_user_attrib[key]
    if int(num_following) > 5000:
      dict_top[user_name]=num_following
    num_requests += ((int(num_following)+4999) /5000)
  time_estimated= (num_requests/60.0) # en hours
  if flag_fast:
    print 'with --fast option only a maximum of 5000 following per user will be used\n'
    print 'time estimated %.2f hours\n' % (num_users/60.0)
  else:
    print 'without the --fast option all following per user will be used\n'
    print 'time estimated %.2f hours\n' % time_estimated
    print 'there are %s users with more than 5.000 following\n' % len(dict_top)
    print 'with --fast option only a maximum of 5000 folowing per user will be used\n'
    print 'with --fast option, time estimated %.2f hours\n' % (num_users/60.0)
  option = raw_input("Continue? (s/n)")
  if option !='s':
    exit(1)
  return

def get_followers_id (api,user,f_log):
  dict_followers={}
  try:
    print 'get %s ids followers' % user
    check_rate_limits (api,'followers','/followers/ids',900)
    for page in tweepy.Cursor(api.followers_ids,screen_name=user).pages():
      check_rate_limits (api,'followers','/followers/ids',900)
      for follower_id in page:
        dict_followers[follower_id]=1
  except:
    f_log.write(('%s, %s error en tweepy, method followers/id, user %s\n')  % (time.asctime(),TypeError(),user))
  return dict_followers

def get_following_id (api,user,f_log,flag_fast):
  dict_following={}
  try:
    print 'get %s ids followings' % user
    check_rate_limits (api,'friends','/friends/ids',900)
    for page in tweepy.Cursor(api.friends_ids,screen_name=user).pages():
      check_rate_limits (api,'friends','/friends/ids',900)
      for following_id in page:
        dict_following[following_id]=1
      if flag_fast:
        break
  except:
    f_log.write(('%s, %s error en tweepy, method friends/id, user %s\n')  % (time.asctime(),TypeError(),user))
  return dict_following

def put_profile (api,user,profile,relation,f_log, f_out):
  location=None
  description=None
  name=None
  timestamp=time.gmtime()
  timestamp_tweet='%s-%s-%s %s:%s:%s' % (timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday,timestamp.tm_hour,timestamp.tm_min,timestamp.tm_sec)
  try:
    location=re.sub('[\r\n\t]+', ' ', profile.location)
    description= re.sub('[\r\n\t]+', ' ', profile.description) 
    name= re.sub('[\r\n\t]+', ' ', profile.name)
  except:
    pass
  f_out.write(('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n') % (profile.id, profile.screen_name,user,relation, profile.followers_count, profile.friends_count, profile.statuses_count,profile.listed_count, profile.created_at, name,profile.time_zone, location,profile.url, profile.profile_image_url,description, timestamp_tweet ))
  f_log.write(('%s:  OK \n')  % (profile.screen_name))
  return

def get_relation (api,user,f_log):
  dict_friends={}
  dict_followers=get_followers_id (api,user,f_log)
  dict_following=get_following_id (api,user,f_log,False)
  for following_id in dict_following:
    if following_id in dict_followers:
      dict_friends[following_id]=1
  print '%s --> %s followers, %s following and %s friends' % (user,len(dict_followers),len(dict_following),len(dict_friends))
  return dict_friends

def get_followers(api,user,dict_friends,f_log,f_out,friends):
  print 'Getting user followers',user
  check_rate_limits (api,'users','/users/show/:id',900)
  profile=api.get_user( screen_name=user)
  num_followers=profile.followers_count
  put_profile (api,user,profile,'root',f_log, f_out)
  followers_getting=0
  try:
    print 'user: %s --> getting %s followers profiles' % (user,num_followers)
    check_rate_limits (api,'followers','/followers/list',900)
    for page in tweepy.Cursor(api.followers,screen_name=user,count=200).pages():
      check_rate_limits (api,'followers','/followers/list',900)
      followers_getting += len(page)
      print 'user: %s --> collected %s followers profiles of %s' % (user,followers_getting,num_followers)
      for profile in page:
        relation='follower'
        if profile.id in dict_friends:
          relation='friend'
        if relation == 'friend' and not friends:
          pass
        else:
          put_profile (api,user,profile,relation,f_log, f_out)
  except:
    f_log.write(('%s, %s error en tweepy, method followers/list, user %s\n')  % (time.asctime(),TypeError(),user))
  return

def get_following (api,user,dict_friends,f_log,f_out,flag_friends):
  print 'Getting user following',user
  check_rate_limits (api,'users','/users/show/:id',900)
  profile=api.get_user( screen_name=user)
  num_following=profile.friends_count
  if flag_friends:
    put_profile (api,user,profile,'root',f_log, f_out)
  following_getting=0
  try:
    print 'user: %s --> getting %s following profiles' % (user,num_following)
    check_rate_limits (api,'friends','/friends/list',900)
    for page in tweepy.Cursor(api.friends,screen_name=user,count=200).pages():
      check_rate_limits (api,'friends','/friends/list',900)
      following_getting += len(page)
      print 'user: %s --> collected %s following profiles of %s' % (user,following_getting,num_following)
      for profile in page:
        relation='following'
        if profile.id in dict_friends:
          relation='friend'
        if relation == 'friend' and not flag_friends:
          pass
        else:
          put_profile (api,user,profile,relation,f_log, f_out)
  except:
    f_log.write(('%s, %s error en tweepy, method friends/list, user %s\n')  % (time.asctime(),TypeError(),user))
  return

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

def get_attrib (f_in):
  i=0
  dict_user_attrib={}
  dict_commons={}
  for line in f_in:
    if i >0:
      data = line.split("\t")
      if len (data) >= 9:
        user_id=int(data[0])
        user_name=data[1]
        if user_id in dict_user_attrib:
          (i_common,user_name,red,relation,num_followers,num_following,num_list,num_statuses,user_TZ) = dict_user_attrib[user_id]
          red='common'
          relation='common'
          dict_user_attrib[user_id]= (i_common,user_name,red,relation,num_followers,num_following,num_list,num_statuses,user_TZ)
          dict_commons[user_id]=1
        else:
          red=data[2]
          relation=data[3]
          num_followers=data[4]
          num_following=data[5]
          num_list=data[6]
          num_statuses=data[7]
          user_TZ=data[8].strip("\n")
          dict_user_attrib[user_id]= (i,user_name,red,relation,num_followers,num_following,num_list,num_statuses,user_TZ)
          i +=1
      else:
        print 'No match',line
    else:
     i +=1
  print '-----------------------------------------------------------\n' 
  print 'there are %s commons users of %s nodes\n' % (len(dict_commons), len(dict_user_attrib))
  return dict_user_attrib

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
  parser.add_argument('--fast', action='store_true', help='get conections faster')
  action = parser.add_mutually_exclusive_group(required=True)
  action.add_argument('--profile', action='store_true',help='get profiles')
  action.add_argument('--followers', action='store_true',help='get followers')
  action.add_argument('--following', action='store_true',help='get following')
  action.add_argument('--relations', action='store_true',help='get relations')
  action.add_argument('--conections', action='store_true',help='get conections')
  action.add_argument('--tweets', action='store_true', help='get tweets')

  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.keys_app
  user_keys_file= args.keys_user
  file_users= args.file_users
  flag_id_user= args.id_user
  flag_fast=args.fast
  flag_profile=args.profile
  flag_followers=args.followers
  flag_following=args.following
  flag_relations=args.relations
  flag_conections=args.conections
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
    print 'File does not exist %s' % file_users
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
    name_file_out= '%s_follower_profiles.txt' % (prefix)
    f_out=  codecs.open(name_file_out, 'w',encoding='utf-8', errors='ignore')
    print "-->Results in %s\n" % name_file_out
    f_out.write ('id user\tscreen_name\tnet\trelation\tfollowers\tfollowing\tstatuses\tlists\tsine\tname\ttime zone\tlocation\tweb\tavatar\tbio\ttimestamp\n')
    print "-->Results in %s\n" % (name_file_out)
    for line in f_users_group_file:
      user= line.strip("\n")
      dict_friends= get_relation (api,user,f_log)
      get_followers (api,user,dict_friends,f_log,f_out,True)
    f_out.close()
  elif flag_following:
    name_file_out= '%s_following_profiles.txt' % (prefix)
    f_out=  codecs.open(name_file_out, 'w',encoding='utf-8', errors='ignore')
    print "-->Results in %s\n" % name_file_out
    f_out.write ('id user\tscreen_name\tnet\trelation\tfollowers\tfollowing\tstatuses\tlists\tsine\tname\ttime zone\tlocation\tweb\tavatar\tbio\ttimestamp\n')
    print "-->Results in %s\n" % (name_file_out)
    for line in f_users_group_file:
      user= line.strip("\n")
      dict_friends= get_relation (api,user,f_log)
      get_following (api,user,dict_friends,f_log,f_out,True)
    f_out.close()
  elif flag_relations:
    name_file_out= '%s_relation_profiles.txt' % (prefix)
    f_out=  codecs.open(name_file_out, 'w',encoding='utf-8', errors='ignore')
    f_out.write ('id user\tscreen_name\tnet\trelation\tfollowers\tfollowing\tstatuses\tlists\tsine\tname\ttime zone\tlocation\tweb\tavatar\tbio\ttimestamp\n')
    print "-->Results in %s\n" % (name_file_out)
    for line in f_users_group_file:
      user= line.strip("\n")
      dict_friends= get_relation (api,user,f_log)
      get_followers (api,user,dict_friends,f_log,f_out,True)
      get_following (api,user,dict_friends,f_log,f_out,False)
    f_out.close()
  elif flag_conections:
    dict_user_attrib= get_attrib(f_users_group_file)
    how_long_it_takes (dict_user_attrib,flag_fast)
    list_user_order=sorted([(value,key) for (key,value) in dict_user_attrib.items()])
    grafo_gdf= Format_gdf(prefix)
    for (value,key) in list_user_order:
      (i,user_name,net,relation,num_followers,num_following,num_list,num_statuses,user_TZ)= value
      print 'looking for following of %s order %s' % (user_name,i)
      grafo_gdf.put_node(i,user_name,net,relation,num_followers,num_following,num_list,num_statuses,user_TZ)
      dict_following=get_following_id(api,user_name,f_log,flag_fast)
      for id_following in dict_following:
        if id_following in dict_user_attrib:
          (i_following,user_following,net,relation,num_followers,num_following,num_list,num_statuses,user_TZ)= dict_user_attrib[id_following]
          grafo_gdf.put_arc(i,i_following)
    grafo_gdf.print_graph()
  elif flag_tweets:
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
