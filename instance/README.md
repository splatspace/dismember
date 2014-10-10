# Flask Instance Data Directory

Dismember starts Flask with the instance\_relative\_config flag set
to true, which means Flask looks in this directory for some files.
This is a good way to do local configuration while developing or
testing, so you don't accidentally commit configuration secrets
to the repo.

## config.py

Create this file and put things in it to override the default values in 
../dismember/config.py file.
