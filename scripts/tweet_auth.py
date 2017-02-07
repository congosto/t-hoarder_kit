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
import webbrowser
import argparse

def get_access_key(keys_app_file, username):
  keys_app=[]
  f = open(keys_app_file, 'rU')
  for line in f: 
    keys_app.append(line.strip('\n'))
   
  auth = tweepy.OAuthHandler(keys_app[0], keys_app[1])
  auth.secure = True

  # Open authorization URL in browser
  webbrowser.open(auth.get_authorization_url())

  # Ask user for verifier pin
  pin = raw_input('Verification pin number from twitter.com: ').strip()

  # Get access token
  (token_key,token_secret) = auth.get_access_token(verifier=pin)
  # Give user the access token
  
  file_out= username+'.key'
  f_out=  open(file_out, 'w')  
  f_out.write ("%s\n" % ( token_key))
  f_out.write ("%s\n" % ( token_secret))
  print 'Access token generado con éxito. Guardado en keys/%s:' % file_out
  return

def main():
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='It gets the  access and secret key of a user')
  parser.add_argument('keys_app', type=str, help='file with app keys')
  parser.add_argument('user', type=str, help='twitter user')
  
  #obtego los argumentos
  args = parser.parse_args()
  keys_app_file=args.keys_app  
  username= args.user 

  get_access_key(keys_app_file, username)
  exit(0)

if __name__ == '__main__':
  main()
