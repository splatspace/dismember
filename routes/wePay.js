var _ = require('underscore');

var config = require('../config/config');
var wePayService = require('../src/wePayService');

function purposeToWePayCheckoutType(purpose) {
  switch (purpose) {
    case 'dues':
    case 'security':
      return 'SERVICE';
    case 'donation':
      return 'DONATION';
    default:
      throw 'Unknown payment purpose ' + purpose;
  }
}

/**
 * Gets the base URI (protocol and host) of the Express request.  Can be instructed
 * to drop the port part, which is useful for constructing WePay callback URIs when
 * testing locally (because WePay rejects URIs that use non-standard ports; use
 * port forwarding from 80 -> 3000 or whatever).
 *
 * @param req the Express request
 * @param {boolean} dropPort if true, the port part (if any) is removed from the host part of the URI
 * @returns {string}
 */
function getBaseUri(req, dropPort) {
  var host = req.get('host');
  if (dropPort) {
    var i = host.indexOf(':');
    if (i != -1) {
      host = host.substring(0, i);
    }
  }
  return req.protocol + '://' + host + config.uriPathPrefix;
}

function getSubmitUri(req) {
  return getBaseUri(req) + '/wepay/submit';
}

function getIpnUri(req) {
  return getBaseUri(req, true) + '/wepay/ipn';
}

/**
 * Serves the index page.
 *
 * @param req
 * @param res
 */
exports.index = function (req, res) {
  res.render('wepay', { title: 'Pay Splat Space with WePay' });
};

/**
 * Handles the HTTP GET that authorizes a payment and starts the flow through WePay.
 *
 * Request parameters required:
 *
 * amount (string that is a dollar amount)
 * type ('dues' | 'donation' | 'security')
 * description (string)
 * payFee (boolean)
 *
 * @param req
 * @param res
 */
exports.authorize = function (req, res) {
  var checkout = {
    accountId: config.wePayAccount.accountId,
    shortDescription: req.query.description,
    type: purposeToWePayCheckoutType(req.query.purpose),
    amount: req.query.amount,
    feePayer: req.query.payFee == 'true' ? 'payer' : 'payee',
    callbackUri:  getIpnUri(req),
    autoCapture: true,

    purpose: req.query.purpose
  }

  // We want to send the user back here after authorizing us at WePay
  var submitUri = getSubmitUri(req);

  wePayService.authorizeCheckout(checkout, submitUri)
    .then(function(authorizeUri) {
      res.redirect(authorizeUri);
    })
    .catch(function (err) {
      console.error(err);
      res
        .status(500)
        .send(err.message);
    });
}

/**
 * Handles the second part of the WePay payment flow.  This is where the redirect URI
 * points in .authorize.
 *
 * @param req
 * @param res
 */
exports.submit = function (req, res) {
  var code = req.query.code;
  var checkoutId = req.query.state;

  wePayService.submitCheckout(checkoutId)
    .then(function (confirmUri) {
      res.redirect(confirmUri);
    })
    .catch(function (err) {
      console.error(err);
      res
        .status(500)
        .send(err);
    });
}

/**
 * Handles an asynchronous POST from WePay about a checkout that has changed state
 * (authorized, settled, etc.).  Expects the parameters that the WePay API docs
 * state will be there.
 *
 * @param req
 * @param res
 */
exports.ipn = function (req, res) {
  wePayService.refreshCheckout(req.body.checkout_id)
    .then(function(checkout) {
      res.send(200);
    })
    .catch(function(err) {
      console.error(err);
      res.send(500);
    });
}