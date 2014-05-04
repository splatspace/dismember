var _ = require('underscore');
var passport = require('passport');

var auth = require('../src/auth');
var config = require('../config/config');

/**
 * Serves the index page.
 *
 * @param req
 * @param res
 */
exports.index = function (req, res) {
  if (!req.user) {
    req.session.loginRedirect = config.uriPathPrefix + '/admin';
    res.redirect('/member/login');
    return;
  }

  req.user.roleEnabled('admin')
    .then(function(enabled) {
      if (enabled) {
        res.render('admin/index', { });
      } else {
        res.send(403);
      }
    });
};
