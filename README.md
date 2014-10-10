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

Once the dependencies are installed, edit config.py to suit your needs.

## Starting the Application

Activate the virtual environment and start the service:

    source ./venv/bin/activate && python service.py

The application will automatically create its database schema when it
starts.

## Running as a Service

On Ubuntu systems, use [upstarter](https://www.npmjs.org/package/upstarter)
to quickly generate an upstart script in /etc/init.  When prompted for commands
to run, enter `source ./venv/bin/activate && python service.py`.  You you get to 
choose the description and the other settings.

On other systems, you'll have to write your own init scripts, but
`cd /where/you/installed/it && source ./venv/bin/activate && python service.py` 
is the critical part.
