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
import sys
#import os.path
import codecs
import argparse

def get_dir (query,path):
  while True:
    dir  = raw_input (query)
    if os.path.isdir('%s%s' % (path,dir)):
      break
    else:
      print '>>>>%s/%s file does not exist' % (path,dir)
  return dir

def get_inputfile (query,path):
  while True:
    file = raw_input (query)
    if os.path.isfile('%s%s' % (path,file)):
      break
    else:
      print '>>>>%s%s file does not exist' % (path,file)
  return file

def get_outputfile (query,path):

  file =raw_input (query)
  print '%s%s' % (path,file)
  if os.path.isfile('%s%s' % (path,file)):
    while True:
      answer= raw_input ('>>>>%s/%s file exists, do you want to append more tweets (y/n)?' % (path,file))
      if answer == 'y':
        return file
      elif answer == 'n':
        return None
      else:
        pass
    else:
      return file
  return file

def get_suboption (query,list_suboptions):
  while True:
    suboption =raw_input (query)
    if suboption in list_suboptions:
      return suboption
    print '>>>>%s Wrong choice, it must be %s' % (suboption,list_suboptions)
  return file

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='menu for t-hoarder_kit')
  parser.add_argument('root', type=str, help='path where t_hoarder_kit was installed')
  action = parser.add_mutually_exclusive_group(required=True)
  action.add_argument('--windows', action='store_true',help='windows OS')
  action.add_argument('--linux', action='store_true',help='linux OS')
  action.add_argument('--mac', action='store_true',help='mac OS')
  args = parser.parse_args()
  root= args.root
  if args.windows:
    path_keys='%s\\keys\\' % root
    path_scripts='%s\\scripts\\' % root
    path_store='%s\\store\\' % root
  if args.linux or args.mac:
    path_keys='%s/keys/' % root
    path_scripts='%s/scripts/' % root
    path_store='%s/store/' % root
  list_suboptions_2= ['profile','followers','following','relations','tweets','h_index']
  list_suboptions_6= ['RT','reply','mentions']
  list_suboptions_7= ['sort','entities','classify','users','spread']
  enviroment=False
  option=8
  exit='n'
  if not enviroment: 
    print  'working in', root
    print  ' '
    print '----------------------------------------'
    print '------>    Environment  data     <------'
    print '----------------------------------------'

    app_keys = get_inputfile ('Enter the file name with the application keys: ', path_keys)
    user = raw_input ('Enter a twitter user: ')
    experiment=get_dir ('Enter experiment name: ', path_store)
    enviroment =True
  file_app_keys= '%s%s' % (path_keys,app_keys)
  file_user_keys= '%s%s.key' % (path_keys,user)
  if args.windows:
    path_experiment = '%s%s\\' % (path_store,experiment)
    path_resources = '%s\resources\\' % (root)
  elif args.linux or args.mac:
    path_experiment='%s%s/' % (path_store,experiment)
    path_resources = '%s/resources/' % (root)

  while exit != 'y':
    try:
      print '--------------------------------'
      print ' Working with:'
      print '   app:',app_keys
      print '   user:',user
      print '   experiment:' ,experiment
      print '--------------------------------'
      print 'What function do you want to run?'
      print '--------------------------------'
      print '1. Get a user token access'
      print '2. Get users information (profile | followers | following | relations | tweets | h_index)'
      print '3. Make a query on Twitter'
      print '4. Get tweets on real time'
      print '5. Generate the declared relations graph (followers or following or both)'
      print '6. Generate the dynamic relations graph (RT | reply | mentions)'
      print '7. Processing tweets (sort |entities| classify| users | spread)'
      print '8. Exit'
      print ' '
      while True:
        try:
          option = int(raw_input('--> Enter option: '))
          break
        except:
          pass
      if option == 1:
        os.chdir(path_keys)
        command="python %stweet_auth.py '%s' '%s'" % (path_scripts,app_keys,user)
        os.system(command)
      elif option ==2:
        os.chdir(path_experiment)
        inputfile=get_inputfile ('Enter input file name with the list of users or list of profiles (each user in a line): ',path_experiment)
        option_rest = get_suboption ('Enter an option (profile | followers | following |relations | tweets| h_index) : ' ,list_suboptions_2)
        if args.windows:
          command="python %stweet_rest.py %s %s %s --%s" % (path_scripts,file_app_keys,file_user_keys, inputfile, option_rest) 
        else:
          command="python %stweet_rest.py '%s' '%s' '%s' '--%s'" % (path_scripts,file_app_keys,file_user_keys, inputfile, option_rest) 
        os.system(command)
      elif option ==3:
        os.chdir(path_experiment)
        query= raw_input ('Enter a query (allows AND / OR connectors): ')
        outputfile= get_outputfile ( 'Enter output file name: ',path_experiment)
        if outputfile != None:
          if args.windows:
            command="python %stweet_search.py %s %s --query %s' --file_out %s" % (path_scripts,file_app_keys,file_user_keys, query,outputfile) 
          else:
            command="python %stweet_search.py '%s' '%s' '--query' '%s' '--file_out' '%s'" % (path_scripts,file_app_keys,file_user_keys, query,outputfile) 
          os.system(command)
        else:
          print 'Option not executed'
      elif option ==4:
        os.chdir(path_experiment)
        file=get_inputfile ('Enter input file name with the keywords separated by , : ', path_experiment)
        outputfile= get_outputfile ('Enter output file name: ', path_experiment)
        if outputfile != None:
          if args.windows:
            command="python %stweet_streaming.py %s %s %s %s  --words %s" % (path_scripts,file_app_keys,file_user_keys,path_experiment, outputfile,file) 
          else:
            command="python %stweet_streaming.py '%s' '%s' '%s' '%s'  '--words' '%s'" % (path_scripts,file_app_keys,file_user_keys,path_experiment, outputfile,file) 
          os.system(command)
        else:
          print 'Option not executed'
      elif option == 5:
        os.chdir(path_experiment)
        inputfile=get_inputfile ('Enter input file name with the users profiles (It is necessary to get before the users profiles): ',path_experiment)
        if args.windows:
          command="python %stweet_rest.py %s %s %s  --connections" % (path_scripts,file_app_keys,file_user_keys, inputfile)
        else:
          command="python %stweet_rest.py '%s' '%s' '%s'  '--connections' " % (path_scripts,file_app_keys,file_user_keys, inputfile)
        fast = raw_input ('opción --fast? (y/n:) ')
        if fast == 'y': 
          if args.windows:
            command=command + '--fast'
          else:
            command=command + '--fast'
        os.system(command)
      elif option == 6:
        os.chdir(path_experiment)
        inputfile =get_inputfile ('Enter input file name with the tweets (got from a query or in real time): ', path_experiment)
        relation= get_suboption ('Enter the relationship type (RT | reply | mention): ',list_suboptions_6)
        top= raw_input ('Introduce top size (100-50000): ')
        if args.windows:
          command="python %stweets_grafo.py %s --%s --top_size %s" % (path_scripts, inputfile, relation,top)
        else:
          command="python %stweets_grafo.py '%s' '--%s' '--top_size' '%s'" % (path_scripts, inputfile, relation,top)
        os.system(command)
      elif option ==7:
        os.chdir(path_experiment)
        option_processing= get_suboption ('Enter option (sort |entities| classify| users | spread): ',list_suboptions_7)
        if option_processing == 'sort':
          inputfile = get_inputfile ('Enter input file name with the tweets (got from a query or in real time): ',path_experiment)
          if args.linux:
            filename, file_extension = os.path.splitext(inputfile)
            if args.windows:
              command='(head -n 1 %s && tail -n +2 %s | sort -u) > %s_ok%s' % (inputfile,inputfile,filename,file_extension)
            else:
              command='(head -n 1 %s && tail -n +2 %s | sort -u) > %s_ok%s' % (inputfile,inputfile,filename,file_extension)
            os.system(command)
            print 'file sorted in  %s_ok%s)' % (filename,file_extension)
          if args.windows:
            print 'in construccion'
        elif option_processing == 'entities':
          inputfile = get_inputfile ('Enter input file name with the tweets (got from a query or in real time): ',path_experiment)
          time_setting = raw_input('Offset GMT time (in Spain 1 in winter, 2 in summer): ')
          if args.windows:
            command="python %stweets_entity.py %s %s %s --top_size 10 --TZ %s" % (path_scripts, inputfile, path_experiment,path_resources,time_setting)
          else:
            command="python %stweets_entity.py '%s' '%s' '%s' '--top_size' '10' '--TZ' '%s'" % (path_scripts, inputfile, path_experiment,path_resources,time_setting)
          os.system(command)
        elif option_processing == 'classify':
          inputfile = get_inputfile ('Enter input file name with the tweets (got from a query or in real time): ',path_experiment)
          topicsfile = get_inputfile ('Enter file name  with topics dictionary: ',path_experiment)
          if args.windows:
            command="python %stweets_classify.py %s %s %s" % (path_scripts, inputfile, topicsfile, path_experiment)
          else:
            command="python %stweets_classify.py '%s' '%s' '%s' " % (path_scripts, inputfile, topicsfile, path_experiment)
          os.system(command)
        elif option_processing == 'users':
          inputfile = get_inputfile ('Enter input file name with the tweets (got from a query or in real time): ',path_experiment)
          if args.windows:
            command="python %susers_types.py %s %s" % (path_scripts, inputfile, path_experiment)
          else:
            command="python %susers_types.py '%s' '%s' " % (path_scripts, inputfile, path_experiment)
          os.system(command)
        elif option_processing == 'spread':
          inputfile = get_inputfile ('Enter input file name with the tweets (got from a query or in real time): ',path_experiment)
          time_setting = raw_input ('Offset GMT time (in Spain 1 in winter, 2 in summer): ')
          if args.windows:
            command="python %stweets_spread.py %s %s --top_size 1000 --TZ %s" % (path_scripts, inputfile, path_experiment, time_setting)
          else:
            command="python %stweets_spread.py '%s' '%s' '--top_size' '1000' '--TZ' '%s' " % (path_scripts, inputfile, path_experiment, time_setting)
          os.system(command)
      elif option == 8:
         exit='y'
    except KeyboardInterrupt:
      pass
    finally:
      pass

if __name__ == '__main__':
   try:
     main()
   except KeyboardInterrupt:
     print '\nGoodbye!'
     exit(0)

