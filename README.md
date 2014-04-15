# dismember

A simple membership and payments web application for Splat Space.

# Installation and Configuration

dismember is a Node.js application that serves HTTP directly.  You could put it
behind a reverse proxy like Apache or nginx, or have it bind to a publically 
accessible port.

## Required Software

- Node.js 0.10.26 or later
- PostgreSQL 9.1 or later

## Setup

First let npm install the dependencies:

    npm install

You might need the PostgreSQL development packages installed to complete
the installation of the "pg" module.

Once the dependencies are installed, copy the config file template and
edit it:

    cp config/config.js.template config/config.js
    vi config/config.js

## Starting the Application

Once you've configured the application, you can start it up with npm:

    npm start

The application will automatically create its database schema when it
starts.

