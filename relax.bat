@echo off
REM Execute this file to run relax in MS Windows.
REM
REM Both relax and python must be located within the system path.
REM This can be set in Windows XP by right clicking on 'My Computer', going to 
REM 'Properties', clicking on the 'Advanced' tab, and clicking on the
REM 'Envirnment Variables' button.  Then double click on the 'Path' system
REM variable and add the text ";C:\Program Files\Python24;C:\relax" to the end
REM of variable value field (modify the text to point to the correct location).

python %~dp0%0 %*