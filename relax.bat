@echo off
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

rem Clear the screen.
cls

rem Run relax using python.  %~dp0 will expand to the path where relax is found
rem and %0 is simply 'relax'.  %* will send all the remaining arguments to
rem relax.
python "%~dp0%0" %*
