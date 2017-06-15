#!/bin/bash
#Copyright 2016 Almudena Garcia Jurado-Centurion

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

option=7
salir='n'
echo " "
echo "----------------------------------------"
echo "------> Welcome to t-hoarder kit <------"
echo "----------------------------------------"
file_t_hoarder_kit=`which t_hoarder_kit.sh`
path_t_hoarder_kit=${file_t_hoarder_kit%/*}
cd $path_t_hoarder_kit
cd  ..
root=`pwd`
cd $root
status=`git status`

if [ ${status} = *"git pull"* ];
then
   echo "There are updates from t-hoarder_kit, do you want to install them (y/n)?"
   read response
   if [ $response = 'y' ];
   then
      echo "Upgrading changes"
      git pull
      chmod +x scripts/*
      echo "t-hoarder_kit is up to date"
      echo " Please, enter <ctrl> c to exit and start again"
   fi
else
  echo "t-hoarder_kit is up to date"
fi

echo "working in ${root}"
echo " "
echo "----------------------------------------"
echo "------>       Environment  data  <------"
echo "----------------------------------------"
while true
do
  echo "Enter the file name with the application keys: "
  read app_key
  if [ -f ${root}/keys/${app_key} ]
  then 
    break
  else
    echo "${root}/keys/${app_key} does not exist"
  fi
done

echo "Enter a twitter user: "
read user

while true
do
  echo "Enter experiment name: "
  read experiment
  if [ -d ${root}/store/${experiment} ]
  then 
    break
  else
    echo "${root}/store/${experiment} does not exist "
  fi
done

while test $salir != 's'
do
    
    echo "------------------------------"
    echo " Working with:"
    echo "   app: ${app_key}"
    echo "   user: ${user}"
    echo "   experiment: ${experiment}"
    echo "------------------------------"
    echo "What function do you want to run?"
    echo "------------------------------"
    echo "1. Get a user's token access"
    echo "2. Get users information (profile | followers | following | relations | tweets | h_index)"
    echo "3. Make a query on Twitter"
    echo "4. Get tweets on real time"
    echo "5. Generate the declared relations graph (followers or following or both)"
    echo "6. Generate the dynamic relations graph (RTs | reply | mentions)"
    echo "7. Processing tweets (entities| classify| users | spread)"
    echo "8. Exit"
    echo " "
    echo "--> Enter option: "
    echo " "

    read option

    case $option in
        1)
            cd keys            
            tweet_auth.py $app_key $usuario
            cd ..
        ;;

        2)
        
            echo "Enter input file name with the list of users (each user in a line): "
            read file
            echo "Enter a type of information (profile | followers | following | relations | tweets | h_index): "
            read option
            tweet_rest.py "./keys/$app_key" "./keys/$usuario.key" "./store/$experiment/$file" --$option 
        ;;

        3)    
            echo "Enter a query (allows AND / OR connectors): "
            read query
            echo "Enter output file name: "
            read outputfile

            tweet_search.py "./keys/$app_key" "./keys/$usuario.key" --query "$query" --file_out "./store/$experiment/$outputfile"
        ;;

        4)
        
            echo "Enter input file name with the keywords separated by , : "
            read file
            echo "Enter output file name: "
            read outputfile

            tweet_streaming.py "./keys/$app_key" "./keys/$usuario.key" "./store/$experiment/" $outputfile --words "./store/$experiment/$outputfile"
        ;;

        5)
        
            echo "Enter input file name with the users profiles (It is necessary to get before the users profiles): "
            read file
            echo "opción --fast? (s/n)"
            read fast
            if [ $fast = 's' ]
            then
              fast='--fast'
            else
              fast=''
            fi

            tweet_rest.py "./keys/$app_key" "./keys/$usuario.key" "./store/$experiment/$file" "--connections" $fast

        ;;
        6)
        
            echo "Enter input file name with the tweets (got from a query or in real time): "
            read file
            echo "Enter the relationship type (RT | reply | mention): "
            read relation
            echo "Introduce top size (100-50000):"
            read top

            tweets_grafo.py "./store/$experiment/$file" "--$relation" "--top_size" $top
        ;;

	7)
            echo "Enter input file name with the tweets (got from a query or in real time): "
            read file
	    echo "Enter option (got from a query or in real time): "
            read option_processing

              case $option_processing in
                  entities)
		  echo "in construccion"
		  ;;
		  classify)
		  echo "in construccion"
		  ;;
		  users)
		  echo "in construccion"
		  ;;
		  spread)
		  echo "in construccion"
		  ;;


              esac
        ;;

        8)
            salir='s'
        ;;
    esac
done


        

    
