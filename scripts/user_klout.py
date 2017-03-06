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
import codecs
import time
from pyklout import Klout
import argparse

class GetKlout(object):
  def __init__(self,APIkey):
     self.api = Klout(APIkey)

  def get_klout (self,user_twitter):
    data = self.api.identity(str(user_twitter), 'tw')
    print data
    user_id = data['id']
    score=self.api.score(user_id)
    return score['score']

def main():
  reload(sys)
  sys.setdefaultencoding('utf-8')
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='Get users Klout ')
  parser.add_argument('file_users', type=str, help='file with list users, one by line')
  parser.add_argument('APIkey', type=str, help='API key de klout')
  args = parser.parse_args()
  file_users= args.file_users
  APIkey= args.APIkey
  filename=re.search(r"([\.]*[\w/-]+)\.([\w]+)",file_users)
  print 'file name', file_users
  if not filename:
    print "bad filename",file_users, ' Must be an extension'
    exit (1)
  prefix=filename.group(1)
  try:  
    f_in = codecs.open(file_users, 'rU',encoding='utf-8')
  except:
    print 'Can not open users file ',file_users
    exit (1)
  f_klout = codecs.open(prefix+'_klout.txt', 'w',encoding='utf-8')
  print 'results in %s_klout.txt\n' % (prefix)
  klout_api=GetKlout(APIkey)
  for line in f_in:
    user=line.rstrip('\r\n')
    if user[0] == '@':
      user=user[1:]
    if True:
    #try:
      klout= klout_api.get_klout(user)
      f_klout.write('%s\t%s\n' % (user,klout))
      print 'user %s: %s klout\n' % (user,klout)
    else:
    #except:
      print 'klout error'
      f_klout.write('%s\tunknow\n' % (user))
      print 'user %s: unknow\n' % (user)
    time.sleep(1)
  f_klout.close()
  exit(0)
 

if __name__ == '__main__':
  main()