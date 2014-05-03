var express = require('express');
var http = require('http');
var path = require('path');
var _ = require('underscore');
var Q = require('q');
var passport = require('passport');
var flash = require('connect-flash');

var config = require('./config/config');
var db = require('./src/db');
var jobs = require('./src/jobs');
var auth = require('./src/auth');

Q.longStackSupport = true;

// Express

var app = express();
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(express.cookieParser());
app.use(express.session({secret: config.sessionCookieSecret}));
app.use(flash());
app.use(passport.initialize());
app.use(passport.session());
app.use(app.router);

if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

// Settings for all views

app.locals.uriPathPrefix = config.uriPathPrefix;
app.locals.ucfirst = function (value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
};

// This is nasty, but there's no easy way to call setMaxListeners on the actual EventEmitter
// instance (the restler request) inside restler-q, so we set it globally.

require('events').EventEmitter.prototype.setMaxListeners(50);

// Web Routes

var wePayRoute = require('./routes/wePay');
app.get('/wepay', wePayRoute.index);
app.get('/wepay/authorize', wePayRoute.authorize);
app.get('/wepay/submit', wePayRoute.submit);
app.post('/wepay/ipn', wePayRoute.ipn);

var memberRoute = require('./routes/member');
app.get('/member', memberRoute.index);
app.get('/member/login', memberRoute.login);
app.post('/member/authenticate', passport.authenticate('local', { successRedirect: '/member/loginSuccess', failureRedirect: '/member/login', failureFlash: "Login failed." }));
app.get('/member/loginSuccess', memberRoute.loginSuccess);
app.get('/member/logout', memberRoute.logout);

var adminRoute = require('./routes/admin');
app.get('/admin', adminRoute.index);

// API Routes

var membersApi = require('./api/members');
app.post('/api/members', function (req, res) {
  membersApi.create(req, res);
});
app.get('/api/members/:id', auth.hasRole('admin', function (req, res) {
  membersApi.get(req, res, req.params.id);
}));
app.get('/api/members', auth.hasRole('admin', function (req, res) {
  membersApi.list(req, res);
}));
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
  .then(db.migrate)
  .then(db.createDefaults)
  .then(jobs.schedule)
  .then(function () {
    auth.configurePassport(passport, db);
  })
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