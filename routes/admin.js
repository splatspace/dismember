var _ = require('underscore');

var auth = require('../src/auth');
var config = require('../config/config');

/**
 * Serves the index page.
 *
 * @param req
 * @param res
 */
exports.index = function (req, res) {
  res.render('admin/index', { title: 'Admin' });
};

/**
 * Serves the login form.
 *
 * @param req
 * @param res
 */
exports.login = function (req, res) {
  res.render('admin/login', { title: 'Login' });
};

/**
 * Logs our the user and serves the logout page.
 *
 * @param req
 * @param res
 */
exports.logout = function (req, res) {
  req.logout();
  res.redirect('/');
}

