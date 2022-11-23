set dest_path=C:\Users\steve\Downloads\Git\KivyMD_test

del %dest_path%\* /q
del %dest_path%\data /q/s/e
rmdir %dest_path%\data /q/s
xcopy "%~dp0\data" "%dest_path%\data" /y /I
xcopy "%~dp0" "%dest_path%" /y
