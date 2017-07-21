@echo off
rem Copyright (C) 2006 Edward d'Auvergne
rem
rem This file is part of the program relax (http://www.nmr-relax.com).
rem
rem This program is free software: you can redistribute it and/or modify
rem it under the terms of the GNU General Public License as published by
rem the Free Software Foundation, either version 3 of the License, or
rem (at your option) any later version.
rem
rem This program is distributed in the hope that it will be useful,
rem but WITHOUT ANY WARRANTY; without even the implied warranty of
rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
rem GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License
rem along with this program.  If not, see <http://www.gnu.org/licenses/>.
rem
rem
rem Execute this file to run relax in MS Windows.
rem
rem Both relax and python must be located within the system path.
rem This can be set in Windows XP by right clicking on 'My Computer', going to 
rem 'Properties', clicking on the 'Advanced' tab, and clicking on the
rem 'Envirnment Variables' button.  Then double click on the 'Path' system
rem variable and add the text ";C:\Program Files\Python24;C:\relax" to the end
rem of variable value field (modify the text to point to the correct location).

rem Attempt to prevent [Ctrl-C] and [Ctrl-Break] form asking "Terminate batch
rem job (Y/N)?" on exit.
break off

rem Run relax using python.  %~dp0 will expand to the path where relax is found.
rem %* will send all the remaining arguments to relax.
python "%~dp0\relax.py" %*
