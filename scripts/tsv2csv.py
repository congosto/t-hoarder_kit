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
from __future__ import print_function
import os
import sys
import codecs
import csv
#import unicodecsv as csv
from imp import reload
import argparse

def main():
  #reload(sys)
  #sys.setdefaultencoding('utf-8')
  #sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
  #defino argumentos de script
  parser = argparse.ArgumentParser(description='This script generates a file in json format for visualization in d3.js')
  parser.add_argument('file_in', type=str, help='file with data')
  parser.add_argument('--size', type=int, default=0, help='num lines')
  parser.add_argument('--num_pack', type=int, default=1, help='num block ini')

  #obtego los argumentos
  args = parser.parse_args()
  file_in=args.file_in
  size=args.size
  num_pack= args.num_pack
  head=True
  try:  
    f_in = codecs.open(file_in, 'rU')
  except:
    print ('Can not open file',file_in)
    exit (1)
  prefix,ext=os.path.splitext(file_in)
  if size == 0:
    f_out=f=codecs.open(prefix+'.csv', 'w',encoding='utf-8',errors='ignore')
  else:
    f_out=f=codecs.open(prefix+'_'+str(num_pack)+'.csv', 'w',encoding='utf-8',errors='ignore')
  writer = csv.writer(f_out,delimiter=',')
  num_line =0
  num_line_block = 0
  for line in f_in:
    line=line.strip('\r\n')
    row=line.split('\t')
    if head:
      row_head=row
      head=False
    if num_line % 10000 == 0:
      print (num_line)
    num_line +=1
    num_line_block += 1
    writer.writerow(row)
    if (size >0) & (num_line_block >= size):
      f_out.close()
      num_pack += 1
      num_line_block =0
      f_out=codecs.open(prefix+'_'+str(num_pack)+'.csv', 'w',encoding='utf-8',errors='ignore')
      writer = csv.writer(f_out,delimiter=',')
      writer.writerow(row_head)
  f_in.close()
  f_out.close()
  print ("converted file %s to %s.csv" % (file_in,prefix))
  exit(0)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print ('\nGoodbye! ')
 