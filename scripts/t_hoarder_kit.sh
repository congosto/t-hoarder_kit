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

opcion=7
salir='n'

cd /home/taller/api_twitter

echo "----------------------------------------"
echo "------>Bienvenido a t-hoarder kit<------"
echo "----------------------------------------"

echo "Escribe el nombre del fichero con las claves de la aplicación: "
read app_key

echo "Escribe el usuario de twitter: "
read usuario

echo "Escribe el experimento: "
read experimento

while test $salir != 's'
do

    echo "------------------------------"
	echo "¿Que operación desea realizar?"
    echo "------------------------------"
	echo "1.Autentificar"
	echo "2.Obtener información de usuarios"
	echo "3.Realizar búsquedas en twitter"
	echo "4.Obtener tweets en tiempo real"
    echo "5.Generar un fichero gdf para gephi"
	echo "6.Salir"
	echo " "
	echo "--> Introduzca número de opción: "
	echo " "

	read opcion

	case $opcion in
		1)
			cd keys			
			tweet_auth.py $app_key $usuario
			cd ..
		;;

		2)
		
			echo "Introduce el nombre del fichero con la lista de usuarios (cada usuario en una línea): "
			read fichero
			echo "Introduce el tipo de información (profile | followers | following | tweets): "
			read option
            tweet_rest.py "./keys/$app_key" "./keys/$usuario.key" "./store/$experimento/$fichero" --$option 
		;;

		3)	
			echo "Introduce palabra a buscar: "
			read palabra
			echo "Introduce el nombre del fichero destino: "
			read fichero

			tweet_search.py "./keys/$app_key" "./keys/$usuario.key" --query "$palabra" --file_out "./store/$experimento/$fichero"
		;;

		4)
		
			echo "Introduce el nombre del fichero con las palabras clave separadas por , : "
			read fichero
			echo "Introduce el nombre del fichero destino: "
			read fich_destino

			tweet_streaming.py "./keys/$app_key" "./keys/$usuario.key" "./store/$experimento/" $fich_destino --words "./store/$experimento/$fichero"

		;;
		5)
		
			echo "Introduce el nombre del fichero con los tweets: "
			read fichero
			echo "Introduce el tipo de relación (RT | reply | mention): "
			read relation
            echo "Introduce top size (100-50000)"
            read top

			tweets_grafo.py "./store/$experimento/$fichero" "--$relation" --top_size $top

		;;

		6)
			salir='s'
		;;
	esac
done


		

	
