::Copyright 2016 Almudena Garcia Jurado-Centurion

::This program is free software: you can redistribute it and/or modify
::it under the terms of the GNU General Public License as published by
::the Free Software Foundation, either version 3 of the License, or
::(at your option) any later version.

::This program is distributed in the hope that it will be useful,
::but WITHOUT ANY WARRANTY; without even the implied warranty of
::MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
::GNU General Public License for more details.

::You should have received a copy of the GNU General Public License
::#along with this program.  If not, see <http://www.gnu.org/licenses/>.

@echo off
echo 
echo -------------------------------
echo -> Welcome to t-hoarder kit <--
echo -------------------------------

set disp=%t-hoarder_kit_HOME:~1,2%
echo dispositivo %disp%
%disp%
cd %t-hoarder_kit_HOME%\scripts%
git fetch origin master  
git status | FIND /C "git pull" > t-hoarder_kit_status.txt
set /P a=< t-hoarder_kit_status.txt
del t-hoarder_kit_status.txt
if %a%==0 (goto uptodate) else (goto askupgrading)
:askupgrading
   set /P upgrading_changes="There are updates from t-hoarder_kit, do you want to install them (y/n)? "
   if %upgrading_changes%==y (goto upgrading) else (goto menu_t-hoarder_kit)
   :upgrading
      echo "Upgrading changes"
      git pull
      echo "t-hoarder_kit is up to date"
      set /P pause=" Please, enter <ctrl> c to exit and start again"
:uptodate
  echo "t-hoarder_kit is up to date"
:menu_t-hoarder_kit
  python %t-hoarder_kit_HOME%\scripts\t_hoarder_menu.py %t-hoarder_kit_HOME% --windows
