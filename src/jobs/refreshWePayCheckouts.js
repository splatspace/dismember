var Q = require('q');
var moment = require('moment');

var db = require('../db');
var wePayService = require('../wePayService');

exports.run = function () {
  // We could miss an IPN, so refresh all the checkouts that are not yet
  // in a terminal state.
  db.WePayCheckout.findAll({
    where: {
      state: ['new', 'authorized', 'reserved', 'captured'],
      wepay_checkout_id: {ne: null}
    }
  })
    .then(function (checkouts) {
      var promises = []
      checkouts.forEach(function (checkout) {
        promises.push(Q.fcall(wePayService.refreshCheckout, checkout.wepay_checkout_id));
      });
      return Q.allSettled(promises)
        .then(function () {
          console.log(checkouts.length + ' active checkouts refreshed');
        });
    })
    .catch(function (err) {
      console.error(err);
    });
}
