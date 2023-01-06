#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# Creative commons 3.0 spain
# http://creativecommons.org/license#!/usr/bin/python
from __future__ import print_function
import sys
import codecs
import re
import simplejson as json
#from tweepy.utils import parse_datetime, parse_html_value, parse_a_href
from imp import reload
import argparse

  
def main():
  #reload(sys)
  #sys.setdefaultencoding('utf-8')
  #sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  parser = argparse.ArgumentParser(description='ls this script classifies users into categories according to their activity')
  parser.add_argument('file_in', type=str, help='file with twarc tweets')
  parser.add_argument('file_out', type=str,default='', help='file with thoarder tweets')
  args = parser.parse_args()
  file_in = args.file_in
  file_out = args.file_out
  dict_users={}
  input_file = codecs.open(file_in,'rU',encoding='utf-8')
  csv_file = codecs.open(file_out, "wb",encoding='utf-8')
  log_file = codecs.open(file_out+'.log', "wb",encoding='utf-8')
  last_line=''
  wrong=False
  count_wrong=0
  num_tweets=0
  csv_file.write ('id tweet\tdate\tauthor\ttext\tapp\tid user\tfollowers\tfollowing\tstauses\tlocation\turls\tgeolocation\tname\tdescription\turl_media\ttype media\tquoted\trelation\treplied_id\tuser replied\tretweeted_id\tuser retweeted\tquoted_id\tuser quoted\tfirst HT\tlang\tcreated_at\tverified\tavatar\tlink\tRTs\treplies\tquotes\tfav\n')
  for line in input_file:
      try:
        object= json.loads(line)
        data = object['data']
        includes = object['includes']
        users = includes['users']
        if 'tweets' in includes:
          tweets_related = includes['tweets']
          size_tweets_related = len (tweets_related)
        else:
          size_tweets_related =0
        size_data = len (data)
        size_users = len (users)
        dict_users ={}
        dict_tweets_related ={}
 # get users data
        for i in range (0,size_users):
          user = users [i]
          location=None
          description=None
          if 'location' in user:
            location=re.sub('[\r\n\t]+', ' ',user['location'],re.UNICODE)
          if 'description' in user:
            description=re.sub('[\r\n\t]+', ' ',user['description'],re.UNICODE)
          id_user =user['id']
          profile = (user[u'username'], user['name'],user['created_at'],description,
                     location,user['public_metrics']['followers_count'],
                     user['public_metrics']['following_count'],user['public_metrics']['tweet_count'],
                     user['verified'],user['profile_image_url'])
          dict_users[id_user] = profile
 # get tweet related
        for i in range (0,size_tweets_related):
          tweet_related = tweets_related [i]
          id_related = tweet_related['id']
          author_id_related = tweet_related ['author_id']
          text_related = re.sub('[\r\n\t]+', ' ',tweet_related ['text'])
          (author,name,since,description,location,followers_count,following_count,tweet_count,verified,avatar) = dict_users [author_id_related]
          dict_tweets_related [id_related] = (author,text_related)
 # get data 
        for i in range (0,size_data):
          num_tweets=num_tweets +1 
          if num_tweets % 10000 == 0:
            print(num_tweets)
  # defauld values
          entities=None
          relation=None
          replied_id=None
          replied_screen_name=None
          retweeted_id=None
          retweeted_screen_name=None
          quoted_id=None
          quoted_screen_name=None
          quoted_text = None
          first_HT=None
          geoloc=None
          url_expanded =None
          url_media=None
          type_media=None
          text=None
          name=None
          RTs =0
          quotes=0
          replies=0
          fav =0
# iteration
          tweet = data [i]
# basic info
          id_tweet=tweet['id']
          author = user['username']
          date = re.sub('T',' ',tweet['created_at'])
          date = re.sub('.000Z',' ',date)
          if 'source' in tweet:
            app=tweet['source']
          else:
            app="None"
#get user profile
          id_user = tweet ['author_id'] 
          (author,name,since,description,location,followers_count,following_count,tweet_count,verified,avatar) = dict_users [id_user]
          since= re.sub('T',' ',since)
          since = re.sub('.000Z',' ',since)
#get interactions Ids
          if 'referenced_tweets' in tweet:
            reference_tweet = tweet['referenced_tweets'][0]
            type_relation = reference_tweet['type']
            id_related = reference_tweet['id']
            if id_related in dict_tweets_related:
               (author_related, text_related) = dict_tweets_related[id_related]
               author_related = '@'+author_related
            else:
              author_related = None
              text_related =None
            if type_relation == 'replied_to':
              relation='reply'
              replied_id= id_related
              replied_screen_name = author_related
            elif type_relation == 'retweeted':
              relation='RT'
              retweeted_id= id_related
              retweeted_screen_name = author_related
            elif type_relation == 'quoted':
              relation='quoted'
              quoted_id= id_related
              quoted_screen_name = author_related
              quoted_text = text_related

#get entities
          if 'entities' in tweet:
            entities=tweet['entities']
            if 'urls' in entities:
              urls=entities['urls']
              if len (urls) >0:
                url_expanded= urls[0]['expanded_url']
            if 'media' in entities:
              list_media=entities['media']
              if len (list_media) >0:
                url_media= list_media[0]['media_url']
                type_media=list_media[0]['type']
            if 'hashtags' in entities:
              HTs=entities['hashtags']
              if len (HTs) >0:
                first_HT=HTs[0]['tag']
#get text
          if 'text' in tweet:
            text=re.sub('[\r\n\t]+', ' ',tweet['text'])
#get quoted if exist
#get metrics 
          if 'public_metrics' in tweet:
            metrics= tweet['public_metrics']
            RTs = metrics ['retweet_count']
            replies=  metrics['reply_count']
            quotes= metrics['quote_count']
            fav =  metrics['like_count']
          link_tweet= 'https://twitter.com/%s/status/%s' % (author,id_tweet)
          tweet='%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %  (id_tweet,
                date,
                '@'+author,
                text,
                app,
                id_user,
                followers_count,
                following_count,
                tweet_count,
                location,
                url_expanded,
                geoloc,
                name,
                description,
                url_media,
                type_media,
                quoted_text,
                relation,
                replied_id,
                replied_screen_name,
                retweeted_id,
                retweeted_screen_name,
                quoted_id,
                quoted_screen_name,
                first_HT,
                tweet['lang'],
                since,
                verified,
                avatar,
                link_tweet,
                RTs,
                replies,
                quotes,
                fav)
          csv_file.write(tweet)
      except Exception as  err:
        str_error=str(err)
        if str_error.find('Unterminated string') != -1:
          last_line=line
          wrong=True
        elif str_error.find('Invalid control') != -1:
          last_line=line[:-1]
          count_wrong +=1
          wrong=True
        else:
          log_file.write('---------------------------------------------\n')
          log_file.write('Exception Error: %s\n' % (str(err)))
          log_file.write('not match %s\n' % (line))

  csv_file.close()
  exit(0) 
if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print('\nGoodbye!')
    exit(0)
