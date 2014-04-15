var express = require('express');
var http = require('http');
var path = require('path');
var _ = require('underscore');
var Q = require('q');

var config = require('./config/config');
var db = require('./src/db');
var jobs = require('./src/jobs');

Q.longStackSupport = true;

// Express

var app = express();
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

// Settings for all views

app.locals.uriPathPrefix = config.uriPathPrefix;

// This is nasty, but there's no easy way to call setMaxListeners on the actual EventEmitter
// instance (the restler request) inside restler-q, so we set it globally.

require('events').EventEmitter.prototype.setMaxListeners(50);

// Web Routes

var wePayRoute = require('./routes/wePay');
app.get('/wepay', wePayRoute.index);
app.get('/wepay/authorize', wePayRoute.authorize);
app.get('/wepay/submit', wePayRoute.submit);
app.post('/wepay/ipn', wePayRoute.ipn);

// API Routes

// TODO enable when we add authentication

//var membersApi = require('./api/members');
//app.post('/api/members', function (req, res) {
//  membersApi.create(req, res);
//});
//app.get('/api/members/:id', function (req, res) {
//  membersApi.get(req, res, req.params.id);
//});
//app.get('/api/members', function (req, res) {
//  membersApi.list(req, res);
//});
//
//
//var paymentsApi = require('./api/payments');
//app.post('/api/payments', function (req, res) {
//  paymentsApi.create(req, res);
//});
//app.get('/api/payments/:id', function (req, res) {
//  paymentsApi.get(req, res, req.params.id);
//});
//app.get('/api/payments', function (req, res) {
//  paymentsApi.list(req, res);
//});

db.sequelize.authenticate()
  .then(db.sync)
  .then(jobs.schedule)
  .then(function () {
    var deferred = Q.defer();
    var server = http.createServer(app);
    server.on('listening', function () {
      deferred.resolve();
    });
    server.on('error', function (err) {
      deferred.reject(err);
    });

    server.listen(app.get('port'));
    return deferred.promise;
  })
  .then(function (port) {
    console.log('Express server listening on port ' + app.get('port'));
  })
  .catch(function (err) {
    console.error(err);
  });