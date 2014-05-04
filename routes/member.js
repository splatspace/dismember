var _ = require('underscore');
var passport = require('passport');

var auth = require('../src/auth');
var config = require('../config/config');
var db = require('../src/db');

/**
 * Serves the index page.
 *
 * @param req
 * @param res
 */
exports.index = function (req, res) {
  if (!req.user) {
    req.session.loginRedirect = config.uriPathPrefix + '/member';
    res.redirect('/member/login');
    return;
  }
  res.render('member/index', { member: req.user });
};

/**
 * Serves the payments page.
 *
 * @param req
 * @param res
 */
exports.payments = function (req, res) {
  if (!req.user) {
    req.session.loginRedirect = config.uriPathPrefix + '/member/payments';
    res.redirect('/member/login');
    return;
  }

  // Nested eager-loads
  db.Member.find({where: { id: req.user.id}, include: [
    {
      model: db.Dues,
      include: [ db.Payment ]
    },
    {
      model: db.Security,
      include: [ db.Payment ]
    },
    {
      model: db.Donation,
      include: [ db.Payment ]
    }
  ],
    order: [
      [ db.Dues, 'period_start', 'desc' ],
      [ db.Security, 'created_at', 'desc' ],
      [ db.Donation, 'created_at', 'desc' ]
    ]
  })
    .then(function (member) {

      // Set the associations on the existing request user so we still have its loaded associations
      req.user.dues = member.dues;
      req.user.securities = member.securities;
      req.user.donations = member.donations;

      res.render('member/payments', { member: req.user });
    });
};

/**
 * Serves the login form.
 *
 * @param req
 * @param res
 */
exports.login = function (req, res) {
  res.render('member/login', {
    flash: req.flash()
  });
};


/**
 * Does the final redirect after the login succeeded.
 *
 * @param req
 * @param res
 */
exports.loginSuccess = function (req, res) {
  var url = req.session.loginRedirect;
  delete req.session.loginRedirect;
  if (!url) {
    url = '/member';
  }
  res.redirect(url);
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

