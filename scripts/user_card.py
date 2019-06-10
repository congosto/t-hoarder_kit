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
import codecs
import locale
import time
import argparse

class oauth_keys(object):
  def __init__(self,  app_keys_file,user_keys_file):
    self.matrix={}
    self.app_keys_file = app_keys_file
    self.user_keys_file = user_keys_file
    self.app_keys=[]
    self.user_keys=[]
    self.dict_ratelimit={}
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
class ProfileCards(object):
  def __init__(self, prefix,list_profiles):
    self.list_profiles=list_profiles
    file_out= '%s_profiles_card.html' % (prefix)
    self.f_out=  codecs.open(file_out,'w',encoding='utf-8')
    return

  def put_profile_card (self,profile):
    root='https://twitter.com/'
    self.f_out.write('      <div class="profile summary">\n')
    self.f_out.write('        <div id="twitter-%s" class="vcard subject">\n' % (profile.screen_name))
    self.f_out.write('          <h2>\n')
    self.f_out.write('            <a class="fn url alternate-context" href="%s" rel="me" target="_blank">\n' % (root+profile.screen_name))
    self.f_out.write('            <img class="photo" src="%s" alt="" width="120" height="120">\n' % (profile.profile_image_url))
    self.f_out.write('            %s</a>\n' % (profile.name))
    self.f_out.write('          </h2>\n')
    self.f_out.write('          <p><span class="nickname">@%s</span></p>\n' % (profile.screen_name))
    self.f_out.write('          <p class="note">%s </p>\n' % (profile.description))
    self.f_out.write('          <div class="stats graph-stats">\n')
    self.f_out.write('            <dl>\n')
    self.f_out.write('               <dt>Desde: </dt>\n')
    self.f_out.write('               <dd class="count">\n')
    self.f_out.write('                %s' % (profile.created_at))
    self.f_out.write('               </dd>\n')
    self.f_out.write('            </dl>\n')
    self.f_out.write('            <dl>\n')
    self.f_out.write('               <dt>Seguidores</dt>\n')
    self.f_out.write('               <dd class="count">\n')
    self.f_out.write('               <a href="%s/followers" class="alternate-context" target="_blank">%s</a>\n' %(root+profile.screen_name,profile.followers_count))
    self.f_out.write('               </dd>\n')
    self.f_out.write('            </dl>\n')
    self.f_out.write('            <dl>\n')
    self.f_out.write('              <dt>Siguiendo</dt>\n')
    self.f_out.write('              <dd class="count">\n')
    self.f_out.write('              <a href="%s/following" class="alternate-context" target="_blank">%s</a>\n' % (root+profile.screen_name,profile.friends_count))
    self.f_out.write('            </dl>\n')
    self.f_out.write('            <dl>\n')
    self.f_out.write('              <dt>Statuses</dt>\n')
    self.f_out.write('              <dd class="count">\n')
    self.f_out.write('              <a href="%s" class="alternate-context" target="_blank">%s</a>\n' % (root+profile.screen_name,profile.statuses_count))
    self.f_out.write('            </dl>\n')
    self.f_out.write('          </div>\n')
    self.f_out.write('        </div>\n')
    self.f_out.write('      </div>\n')
    return

  def put_profiles (self):
    self.f_out.write ('<html>\n')
    self.f_out.write ('<head>\n')
    self.f_out.write ('<meta charset="utf-8">\n')
    self.f_out.write ('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">\n')
    self.f_out.write ('<link rel="stylesheet" href="https://abs.twimg.com/a/1520469656/css/tfw/intents_rosetta.bundle.css">\n')
    self.f_out.write ('</head>\n')
    self.f_out.write ('<body>\n')
    self.f_out.write ('<div class="container">\n')
    i=0
    self.f_out.write ('  <div class="row">\n')
    for profile in self.list_profiles:
      if (i % 2 == 0) and (i >0):
        i +=1
        self.f_out.write ('  </div>\n')
        self.f_out.write ('  <div class="row">\n')
      self.f_out.write ('    <div class="col-sm">\n')
      self.put_profile_card (profile)
      self.f_out.write ('    </div>\n')
    self.f_out.write ('  </div>\n')
    self.f_out.write ('  </div>\n')
    self.f_out.write ('</body>\n')
    self.f_out.write ('</html>\n')
    self.f_out.close()
    return

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  locale.setlocale(locale.LC_ALL, 'es_ES.utf-8')
  list_profiles=[]
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Examples usage Twitter API REST')
  parser.add_argument('keys_app', type=str, help='file with app keys')
  parser.add_argument('keys_users', type=str, help='file with user keys')
  parser.add_argument('file_users', type=str, help='file with list users')

  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.keys_app
  user_keys_file=args.keys_users
  file_users= args.file_users
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
  for line in f_users_group_file:
    user= line.rstrip('\r\n')
    oauth_keys.check_rate_limits (user_keys,api,'users','/users/show/:id',900)
    try:
      print 'collected profile of %s \n' % user
      profile=api.get_user(user_keys, screen_name=user)
      list_profiles.append(profile)
    except:
      print 'wrong profile of %s  \n' % user
  cards=ProfileCards(prefix,list_profiles)
  cards.put_profiles()
 
if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye! '