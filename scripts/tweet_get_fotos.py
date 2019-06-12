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
import httplib
import urlparse
import requests
import time
from datetime import datetime
import codecs
import argparse
import csv
import unicodecsv as csv

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

def put_html (list_tweets_by_day,dict_photos,dir_out,f_out,top):
    f_out.write ('<html>\n')
    f_out.write ('<head>\n')
    f_out.write ('<meta charset="UTF-8">\n')
    f_out.write ('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">\n')
    f_out.write ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">\n')
    f_out.write ('</head>\n')
    f_out.write ('<body>\n')
    f_out.write ('<table>\n')
    n_tweets=0
    head=True
    for (date,author,text,RTs,id_tweet,permanent_link,meta_img) in list_tweets_by_day:
      if head:
       f_out.write ('<h3>Photos most retweeted on %s</h3>\n' % (date))
       head =False
      f_out.write ('<tr >\n<td width="50%%"><strong>fecha:</strong> %s<br/><strong>author:</strong> %s<br/><strong>texto:</strong>%s<br/><strong>RTs:</strong> %s<br><strong>id_tweet:</strong> %s</br><strong>permanent_link:</strong> <a href="%s">%s</a><br/></td>\n' % (date,author,text,RTs,id_tweet,permanent_link, permanent_link))
      if meta_img != '':
        f_out.write ('<td with="50%%"><img src=%s/photos/%s width=300></td>\n</tr>\n' % (dir_out,meta_img))
      else:
        f_out.write ('<td with="50%%"> Sin imagen</td>\n</tr>\n')
      f_out.write ('<tr><td><hr/></td><td><hr/></td</tr>\n')
      n_tweets += 1
      if n_tweets > top:
        break
    f_out.write ('</table>')
    f_out.write ('</body>\n')
    f_out.write ('</html>\n')
    f_out.close()
    return

def unshorten_url(url):
  parsed = urlparse.urlparse(url)
  h = httplib.HTTPConnection(parsed.netloc)
  h.request('HEAD', parsed.path)
  response = h.getresponse()
  #try:
  session = requests.Session()  # so connections are recycled
  resp = session.head(url, allow_redirects=True,timeout=30)
  print 'requests.Session'
  return resp.url
  #except:
  #print 'fail ',url
  #return "None"

def is_there_photo (statuse):
  url_media=None
  type_media=None
  id_tweet=statuse.id_str
  #get entities
  if hasattr (statuse,'entities'):
    entities=statuse.entities
  if hasattr (statuse,'retweeted_status'):
    if hasattr (statuse.retweeted_status,'entities'):
      entities=statuse.retweeted_status.entities
  if entities != None:
    if True:
    #try:
      if 'media' in entities:
       list_media=entities['media']
       if len (list_media) >0:
         url_media= list_media[0]['media_url']
         type_media=list_media[0]['type']
         if type_media == 'photo':
           return (id_tweet,url_media)
    else:
   #except:
      text_error = '---------------->bad entity Media, id tweet %s at %s\n' % (id_tweet,time.asctime())
      f_log.write (text_error)
  return(None,None)

def get_photos_by_id_tweet(user_keys,api,file_in,dir_out,top):
  list_tweets_by_day=[]
  dict_tweets=[]
  dict_photos={}
  filename=re.search (r"([\w-]+)\.([\w\.]*)", file_in)
  print 'file name', file_in
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  name=filename.group(0)
  prefix=filename.group(1)
  extension=filename.group(2)
  print extension
  try:
    f_in = codecs.open(file_in, 'rU',encoding='utf-8')
    print 'open as unicode'
  except:
    print 'Can not open file',file_in
    exit (1)
  f_out=  codecs.open(dir_out+'/'+prefix+'_photos.html','w',encoding='utf-8')
  f_log= open(dir_out+'/'+prefix+'.log','w')
  print "-->Results in %s_fotos_by_id.txt\n" % prefix
  head=True
  n_tweets=0
  for line in f_in:
    line= line.strip('\n')
    data= line.split('\t')
    timestamp=  data[0]
    aux=timestamp.split (' ')
    day=aux[0].replace('/','-')
    author= data[1]
    text= data [2]
    RTs= data [3]
    id_tweet= data[4]
    permanent_link= 'https://twitter.com/%s/status/%s' % (author[1:],id_tweet)
    meta_img=''
    url_media=None
    if id_tweet not in dict_photos:
      oauth_keys.check_rate_limits (user_keys,api,'statuses','/statuses/show/:id',900)
      try:
        statuse=api.get_status(id=id_tweet,include_rts=1,include_entities=1,tweet_mode='extended')
        (id_tweet,url_media)=is_there_photo (statuse)
      except:
        text_error = '---------------->no exist at %s id tweet %s \n' % (time.asctime(),line)
        f_log.write (text_error)
      if url_media != None:
        img=os.path.basename(url_media)
        meta_img='%s-%05d-%s-%s' % (day,int(RTs),author,img)
        command= 'ls %s/photos/%s' % (dir_out,meta_img)
        print command
        result= os.system(command)
        if result == 0:
          print 'file %s exist' % (meta_img)
        else:
          command= 'wget %s -P %s' % (url_media,dir_out)
          print command
          status=os.system(command)
          count=0
          while status != 0:
            print 'fail' ,url_media
            status=os.system(command)
            count += 1
            if count > 10:
              img=None
            break
          if img !=None:
            meta_img='%s-%05d-%s-%s' % (day,int(RTs),author,img)
            command='mv %s/%s %s/photos/%s' % (dir_out,img,dir_out,meta_img)
            status=os.system(command)
            count=0
            while status != 0:
              print 'fail',command
              time.sleep(1)
              status=os.system(command)
              count += 1
              if count > 10:
                break
        dict_photos[id_tweet]=meta_img
        n_tweets= n_tweets +1
        if n_tweets % 100 ==0:
          print 'get ',n_tweets, 'photos'
    else:
      meta_img= dict_photos[id_tweet]
    list_tweets_by_day.append (( timestamp,author,text,RTs,id_tweet,permanent_link,meta_img))
  put_html (list_tweets_by_day,dict_photos,dir_out,f_out,len(list_tweets_by_day))
  return

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  ini_key=4
  num_keys=30
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Examples usage Twitter API REST, search method')
  parser.add_argument('keys_app', type=str, help='file with app keys')
  parser.add_argument('keys_user', type=str, help='file with user keys')
  parser.add_argument('file_in', type=str, help='name file in with id_tweet')
  parser.add_argument('--dir_out', type=str, default='./', help='Dir data output')
  parser.add_argument('--top', type=str, default='50', help='top for summary')
  #obtego los argumentos
  args = parser.parse_args()
  app_keys_file= args.keys_app
  user_keys_file= args.keys_user
  dir_out=args.dir_out
  file_in= args.file_in
  top= int(args.top)
  command='mkdir %s/photos' % (dir_out)
  status=os.system(command)
  #print query,file_out
  #autenticación con oAuth     
  user_keys= oauth_keys(app_keys_file,user_keys_file)
  api= oauth_keys.get_access(user_keys)

  get_photos_by_id_tweet(user_keys,api,file_in,dir_out,top)
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
