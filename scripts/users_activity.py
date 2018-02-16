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
from datetime import timedelta
import unicodedata
import math
import codecs

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
class AvgDict(dict):
    def __init__(self):
        self._total = 0.0
        self._count = 0

    def __setitem__(self, k, v):
        if k in self:
            self._total -= self[k]
            self._count -= 1
        dict.__setitem__(self, k, v)
        self._total += v
        self._count += 1

    def __delitem__(self, k):
        v = self[k]
        dict.__delitem__(self, k)
        self._total -= v
        self._count -= 1

    def store (self,k,v):
        if k not in self:
          self[k]=v
          self._count += 1
        else:
          old_value=self[k]
          self[k]=old_value+v
        self._total += v
        return 

    def store_unique (self,k,v):
      if k not in self:
        self[k]=v
        self._count += 1
        self._total = v
        return   

    def getitem (self,k):
      if k not in self:
        return 0
      else:
        return self[k]

    def average(self):
        if self._count:
            return self._total/self._count

    def total(self):
        total_v =0
        for v in self:
          total_v += v
        return total_v

    def reset(self):
        self._total = 0.0
        self._count = 0
        return

class Matrix(dict):
  def __init__(self):
    return
 
  def setitem(self, row, col, v):
      dict.__setitem__(self,(row,col),v)
      return

  def getitem(self, row,col):
    if (row,col) not in self:
      return 0
    else:
      return self[(row,col)]  
 
  def store(self, row, col, v):
    if (row,col) not in self:
      dict.__setitem__(self,(row,col),v)
    else:
       old_value=self[(row,col)] 
       dict.__setitem__(self,(row,col),v+old_value)
    return

  def store_unique(self, row, col, v):
    if (row,col) not in self:
      dict.__setitem__(self,(row,col),v)
    return 
    
class SpreadSheet (object):
  def __init__(self,  prefix):
    self.prefix=prefix
    self.style_cab = easyxf('font: name Verdana, color-index black, bold on; align: wrap on, vert centre, horiz center',	num_format_str='#,##0')
    self.style_char_num = easyxf('font: name Verdana, color-index black', num_format_str='#,##0')
    self.style_date = easyxf(num_format_str='YYYY-MM-DD') 
    self.wb= Workbook('utf-8')
  def new_sheet (self,name,headers): 
    self.i=0
    j=0
    print 'creating sheet ',name
    self.ws = self.wb.add_sheet(name)
    for head in headers:
      self.ws.write(self.i,j,head, self.style_cab)
      j +=1
    self.i += 1
    return 

  def write_row (self,list_data,type_data): 
    #write cab
    j=0
    for data in list_data:
      if type_data == 'text':
        self.ws.write(self.i,j,data,self.style_char_num)
      elif type_data =='formula':
        self.ws.write(self.i,j,Formula(data),self.style_char_num)
      j += 1
    self.i += 1
    return
 
  def save_wb(self):
    self.wb.save(self.prefix+'.xls') 
    return 

class Profilesplus(object):
  def __init__(self,  file_profiles,prefix):
    self.prefix=prefix
    self.dict_users={}
    self.list_users=[]
    self.num_users=0
    self.num_profiles=0
    
    try:  
      f_in = codecs.open(file_profiles, 'rU',encoding='utf-8')
    except:
      print 'Can not open file profiles ',file_profiles
      exit (1)
    for line in f_in:
      #print line
      line= line.strip("\n")
      data = line.split("\t")
      self.num_users += 1
      user_id=data[0]
      user_name=data[1].lower()
      name=data[2]
      followers=data[3]
      following=data[4]
      tweets=data[5]
      lists=data[6]
      since=data[7]
      identity=data[8]
      gender=data[9]
      age=data[10]
      type_user=data[11]
      profession=data[12]
      sector=data[13]
      subsector=data[14]
      level=data[15]
      location=data[16]
      country=data[17]
      region=data[18]
      provincia=data[19]
      city=data[20]
      urban_local=data[21]
      self.dict_users[user_id]=(user_id,user_name,name,followers,following,tweets,lists,since,identity,gender,age,type_user,profession,sector,subsector,level,location,country,region,provincia,city,urban_local)
      self.list_users.append(user_id)
      self.num_profiles +=1
    return

  def get_profile(self,user_id):
    if user_id in self.dict_users:
      return self.dict_users[user_id]
    else:
      print user_id, 'profile unknow'
      return 'unknow'
  def print_profile (self,user_id):
    (user_id,user_name,name,followers,following,tweets,lists,since,identity,gender,age,type_user,profession,sector,subsector,level,location,country,region,provincia,city,urban_local)= self.dict_users[user_id]
    text_profile='%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t' % (user_id,user_name, name,followers,following,tweets,lists,since,identity,gender,age,type_user,profession,sector,subsector,level,location,country,region,provincia,city,urban_local)
    return text_profile
    
  def get_list_users(self):
    return self.list_users

class TweetsActivity(object):
  def __init__():
    self.dict_hashtags=Matrix() #top-ten hashtags
    self.tweets=AvgDict()
    self.dict_RT_in=AvgDict()
    self.dict_RT_out=AvgDict()
    self.dict_metions_in=AvgDict()
    self.dict_mentions_out=AvgDict()
    self.dict_replies_in=AvgDict()
    self.dict_replies_out=AvgDict()
    self.num_users=0
    self.dict_users={}
    self.dict_users_app={}
    self.dict_users_followers={}
    self.dict_users_following={}
    self.dict_users_location={}
    self.dict_users_url=AvgDict()
    self.dict_users_name={}
    self.dict_users_bio={}
    self.dict_users_url_media=AvgDict()
    self.dict_users_ht=AvgDict()

  def token_hashtags (self,source):
    source=strip_accents (source)
    list_tokens=re.findall (r'#\w+', source,re.U)
    return list_tokens

  def get_relation(self,statuse):
    relations=[]
    list_mentions=re.findall (r'@\w+', statuse)
    if len(list_mentions) == 0:
      return('None',relations)
    else:
      if re.match(r'[\.]*(@\w+)[^\t\n]+',statuse):
        relations.append (list_mentions[0])
        return ('@', relations)
      elif re.match('[RT[\s]*(@\w+)[:]*',statuse,re.U):
        relations.append (list_mentions[0])
        return ('rt',relations)
      else:  
        for mention in list_mentions:
          relations.append (mention)
        return ('mentions',relations)


  def get_urls (self,statuse):
    urls=re.findall (r'(http[s]*://\S+)', statuse,re.U)
    return urls
  
  def class_tweet (self,tweet_flat):
     (id_tweet,year,month,day,hour,minutes,seconds, author,text,app,id_user,followers,following,stauses,location,url,geolocation,name,description,url_media) =tweet_flat
    # guarda el primer Tweet
    found_date=False
    if user not in self.dict_users:
      self.num_users +=1
      self.dict_users[user]= id_user
      self.dict_users_app[user]=app
      self.dict_users_followers[user] = followers 
      self.dict_users_following[user] = following
      self.dict_users_location[user] = location
      self.dict_users_name[user] = name
      self.dict_users_bio[user] = description
      if url != None:
        self.dict_users_url.store(user,1)

      if url_media != None:
        self.dict_users_url_media.store(user,1)
          
      for (from_date,to_date) in  self.dict_groups:
        if (date >= from_date) and (date <= to_date):
          self.dict_first_tweet[user]=self.dict_groups[from_date,to_date]
          found_date=True
          break
      if not found_date:    
        print 'date not found:', date
    # guarda tweets por usuario
    self.tweets.store(user,1)
    # guarda tweets por usuario y dia
    self.tweets_by_day.store(user,date,1)
    if date not in self.days:
      self.days.append(date)
    # uso del top-ten hashtags por usuario
    list_hashtags=self.token_hashtags(text)
    for hashtag in list_hashtags:
      if hashtag in self.list_hashtags:
        self.dict_hashtags.store(user,hashtag,1)
      else:
        self.dict_hashtags.store(user,'Other',1)
   # clasifica el tweet (text,hashtag,url,url+hashtag,RT,talk,mention)
    (relation,list_relations)=self.get_relation(text)
    urls=self.get_urls(text)
    if relation =='rt':
      self.dict_class_tweet.store(user,'rt',1)
    elif relation == '@':
      self.dict_class_tweet.store(user,'@',1)
    elif len(urls) >0 & len (list_hashtags) >0:
      self.dict_class_tweet.store(user,'hashtag+url',1)
    elif len (urls) > 0:
      self.dict_class_tweet.store(user,'url',1)
    elif len (list_hashtags) >0:
      self.dict_class_tweet.store(user,'hashtag',1)
    elif len(list_relations) == 0:
      self.dict_class_tweet.store(user,'text',1)
  # guarda RT-in /RT- out por usuario 
    if relation =='rt':
      self.dict_RT_in.store(list_relations[0],1)
      self.dict_RT_out.store(user,1)
  # guarda replies por usuario
    if relation =='@':
      self.dict_replies_in.store(list_relations[0],1)
      self.dict_replies_out.store(user,1)
    return
  
  def join_at (self, user):
  #Tipo de incorporación (pionero, boom,tardío)
    if user in self.dict_first_tweet:
      return self.dict_first_tweet[user]
    else:
      pass
      print 'user unknow',user
    return 'unknow'
  
  def hashting_as (self, user):
  #top-ten hashtags
    max_hashtag=0
    num_hashtags=0
    top_hashtag=''
    for hashtag in self.list_hashtags:
      count_hashtags=self.dict_hashtags.getitem(user,hashtag)
      if  count_hashtags > 0:
        num_hashtags +=1
        if count_hashtags > max_hashtag:
          max_hashtag= count_hashtags
          top_hashtag= hashtag
    if num_hashtags > 0:
      self.top_hashtags[user]=(top_hashtag,num_hashtags)
      return (top_hashtag,num_hashtags)
    #print top_hashtag 
    return (u'Other',0)
  
    
  def perfil (self, user):
  
  #  perfil
 
    if (self.dict_RT_out.getitem(user) == 0) and (self.dict_RT_in.getitem(user) == 0):
    #    Isolated ( No RT_IN no RT-OUT))
      self.class_profile[user]='Isolated'
      return self.class_profile[user]
    elif self.dict_RT_out.getitem(user) == 0:
      self.dict_RT_out.store(user,1)  #para poder calcular los coeficientes
    elif self.tweets.getitem(user) ==0:
      self.tweets.store(user,1) #para poder calcular coeficientes
    num_tweets= self.tweets.getitem (user)
    average_tweets=self.tweets.average ()
    k_rt=(self.dict_RT_in.getitem(user)*1.0)/self.dict_RT_out.getitem(user)
    k_out=(self.dict_RT_out.getitem(user)*1.0)/num_tweets
    k_in=(self.dict_RT_in.getitem(user)*1.0)/ num_tweets
    
      #    Opinion leader (++ RT-IN)
    if k_in > 4: 
      self.class_profile[user]='Influencer'
    #    transmitter (++RT-OUT)
    elif (num_tweets >= average_tweets) and (k_rt >= 0.85):
      self.class_profile[user]='Networker' 
    elif  (num_tweets >= average_tweets) and (k_out >= 0.40):
      self.class_profile[user]='Resonator'
    #    Networking (++RT-In, ++RT-OUT)
    elif  num_tweets >= average_tweets:
      self.class_profile[user]='Monologist'
    else: 
      self.class_profile[user]='Passive'
    #print user, num_tweets,self.dict_RT_in.getitem(user),self.dict_RT_out.getitem(user),k_rt,k_in,k_out,  self.class_profile[user] 
    return self.class_profile[user]
  
  def activity (self, user):
  #  Indice de actividad: (alta,media,baja)
    num_tweets=0
    num_days=0
    total_days= len (self.days)
    for day in self.days:
      if self.tweets_by_day.getitem(user,day) >0:
        num_tweets += self.tweets_by_day.getitem(user,day)
        num_days +=1 
    if num_tweets/total_days > 5:
      self.volume[user]='Volume high'
    elif num_tweets/total_days > 0.5:
      self.volume[user]='Volume medium'
    else:
     self.volume[user]='Volume low'
  
  #  Persistencia (alta,media,baja)
  
    if num_days > (total_days * 0.5):
      self.persistence[user]='Persistence high'
    elif num_days > (total_days* 0.2):
      self.persistence[user]='Persistence medium'
    else:
      self.persistence[user]='Persistence low' 
    
    return (self.volume[user], self.persistence[user])
    
  def get_statistics(self,num_users_group):  
    
    f_log=codecs.open(self.prefix+'.log', 'a',encoding='utf-8',errors='ignore')
    groups=AvgDict()
    num_users=len(self.dict_first_tweet)
    print 'num users:',num_users
    for group in self.dict_first_tweet:
      groups.store(self.dict_first_tweet[group],1)
    for group in groups:
      per_group = (groups[group] *100.0)/num_users
      print  "Group %s, %.2f" % (group, per_group)
      f_log.write ("Group %s, %.2f \n" % (group, per_group))
      
    hashtags=AvgDict()  
    for user in self.top_hashtags:
      (hashtag,num) = self.top_hashtags[user]
      hashtags.store (hashtag,1)
    for hashtag in hashtags:
      per_hashtag = (hashtags[hashtag] *100.0)/num_users_group
      print  "hashtag %s, %.2f" % (hashtag, per_hashtag)
      f_log.write ("hashtag %s, %.2f \n" % (hashtag, per_hashtag))
      
    volume=AvgDict()  
    for user in self.volume:
      activity = self.volume[user]
      volume.store (activity,1)
    for activity in volume:
      per_activity = (volume[activity] *100.0)/num_users_group
      print  "volume %s, %.2f" % (activity, per_activity)
      f_log.write ("volume %s, %.2f \n" % (activity, per_activity))
      
    persistence=AvgDict()  
    for user in self.persistence:
      activity = self.persistence[user]
      persistence.store (activity,1)
    for activity in persistence:
      per_persistence = (persistence[activity] *100.0)/num_users_group
      print  "Persistence %s, %.2f" % (activity, per_persistence)
      f_log.write ("Persistence %s, %.2f \n" % (activity, per_persistence))
      
    perfiles=AvgDict()  
    for user in self.class_profile:
      perfil = self.class_profile[user]
      perfiles.store (perfil,1)
    for perfil in perfiles:
      per_perfil = (perfiles[perfil] *100.0)/num_users_group
      print  "Class profile %s, %.2f" % (perfil, per_perfil)
      f_log.write ("Class profile %s, %.2f \n" % (perfil, per_perfil))
    return
    
      
  def  get_list_join(self):
    return ["Early","Boom","Late"]
    
  def get_list_hashtags(self):
   return self.list_hashtags
   
  def get_list_perfiles(self):
   return ["Opinion leader","Networker","Transmitter","Pasive","Isolated"]
  
  def get_list_volume(self):
   return ["Volume high","Volume medium","Volume low"]
  
  def get_list_persistence(self):
   return ["Persistence high","Persistence medium","Persistence low"]
   
  def get_media(self):
      
    print 'media de tweets por usuario %.2f' % self.tweets.average()
    print 'media de RTs_in por usuario %.2f' % self.dict_RT_in.average()
    print 'media de RTs_out por usuario %.2f'% self.dict_RT_out.average()
    print 'media de replies_in por usuario %.2f' % self.dict_replies_in.average()
    print 'media de replies_out por usuario %.2f' %self.dict_replies_out.average()
    return
id tweet	date	author	text	app	id user	followers	following	stauses	location	urls	geolocation	name	description	url_media	type media	quoted
def get_tweet (tweet):
   data = tweet.split('\t')
   try:
     id_tweet = data[0]
     timestamp = data[1]
     date_hour =re.findall(r'(\d\d\d\d)-(\d\d)-(\d\d)\s(\d\d):(\d\d):(\d\d)',timestamp,re.U)
     (year,month,day,hour,minutes,seconds) = date_hour[0]
     author= data[2]
     text = data[3]
     app = data[4]
     id_user = data[5]
     followers = data[6]
     following = data [7]
     statuses = data[8]
     location = data[9]
     urls = data[10]
     geolocation= data[11]
     name = description= data[12]
     url_media = data[13]
     return (id_tweet,year,month,day,hour,minutes,seconds, author,text,app,id_user,followers,following,stauses,location,urls,geolocation,name,description,url_media)
   except:
     print 'tweet not match'
     return None

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Getting entities')
  parser.add_argument('file_in', type=str, help='File with the tweets')
  parser.add_argument('path_experiment', type=str,default='', help='Dir experient')
  parser.add_argument('path_resources', type=str,default='', help='Dir experient')
  #get arguments
  args = parser.parse_args()
  file_in= args.file_in
  path_experiment= args.path_experiment
  path_resources=args.path_resources
  head = True
  first_tweet=True
  num_users=0
  num_tweets=0

  filename=re.search (r"([\w-]+)\.([\w]*)", file_in)
  print 'file name', file_in
  if not filename:
    print "bad filename",file_in, ' Must be an extension'
    exit (1)
  name=filename.group(0)
  prefix=filename.group(1)

  demography=Demography(path_resources)
  activity= TweetsActivity()
  #analize Tweets
  try:  
    f_in = codecs.open(file_in, 'rU',encoding='utf-8')
  except:
    print 'Can not open file',file_in
    exit (1)
  f_out = codecs.open(prefix+'_users.txt', 'w',encoding='utf-8')
 
  for line in f_in:
    if head:
      head=False
    else:
      tweet_flat= get_tweet(line)
      if tweet_flat == None:
        print 'not match '
      else:
        (id_tweet,year,month,day,hour,minutes,seconds, author,text,app,id_user,followers,following,stauses,location,urls,geolocation,name,description,url_media)= tweet_flat
        if num_tweets % 10000 == 0:
          print num_tweets  
        author=author.lower()
        text=text.lower()
        loc=loc.lower()
        activity.class_tweet (tweet_flat)
  list_users=activity.get_users ()
  f_out.write('User Role\tFollowers/Following\tRatio RT_in\tratio_RT_out\tRatio multimedia\tRatio URL\tRatio HT\tGender\tApp\tlocation\Provincia\Region\Bio\n')
  for user_id in list_users:
    num_users +=1
    role=activity.role(user)
    FF=activity.FF(users)
    ratio_RT_in=  activity.ratio_RT_in(user)
    ratio_RT_out= activity.ratio_RT_out(user)
    ratio_multimedia= activity.ratio_multimedia (user)
    ratio_url= activity.ratio_multimedia (user)
    ratio_HT= activity.ratio_multimedia (user)
    app=activity.name (user)
    name = activity.name (user)
    location = activity.location (user)
    bio=activity.bio (user)
    gender = demography.gender(name)
    (location,provincia,area) =  demography.gender(location)
     f_out.write ('' %( user,role,FF,ratio_RT_in,ratio_RT_out,ratio_multimedia,ratio_url,ratio_HT,gender,app,location,provincia,area,bio
  f_out.close() 
  exit(0)

if __name__ == '__main__':
  main()
   try:
    main()
  except KeyboardInterrupt:
    print '\nGoodbye!'
    exit(0)
