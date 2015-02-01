# dismember

A simple membership and payments web application for Splat Space.

# Installation and Configuration

dismember is a web application written in Python that uses the Flask 
web microframework.  You could put it behind a reverse proxy like Apache or 
nginx, or have it bind to a publically accessible port.

virtualenv is used to manage dependencies, so you don't have to install
them system-wide.

## Required Software

- Python 2.7
- pip
- virtualenv
- PostgreSQL 9.1+

## Setup

First install the Python dependencies:

    sudo apt-get install python-pip python-virtualenv

Then install the dependencies into the current directory:

    ./vinstall

You might need the PostgreSQL development packages installed to complete
the installation of the PostgreSQL driver.

## Configuration

First create a configuration file in the instance directory:

    cp ./dismember/config.py ./instance/config.py
     
Then edit ./instance/config.py to suit your needs.  Settings in this file
override settings in the default config.py (the file you made a copy of).

## Starting the Application

Activate the virtual environment and start the service:

    source ./venv/bin/activate && python service.py

The application creates missing database tables and types (enums, etc.) when it
starts.  Tables and types that already exist are not altered, but the application
starts anyway.

In the future we should use a schema migration tool.

## Running as a Service

On Ubuntu systems, use [upstarter](https://www.npmjs.org/package/upstarter)
to quickly generate an upstart script in /etc/init.  When prompted for commands
to run, enter `source ./venv/bin/activate && python service.py`.  You you get to 
choose the description and the other settings.

On other systems, you'll have to write your own init scripts, but
`cd /where/you/installed/it && source ./venv/bin/activate && python service.py` 
is the critical part.
