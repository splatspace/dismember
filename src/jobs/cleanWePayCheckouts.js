var moment = require('moment');
var db = require('../db');

exports.run = function () {
  // Checkout codes are only good for 10 minutes.  If a user doesn't complete the
  // checkout by then, we can delete the checkout row in the database.
  var time = moment.utc().add('minutes', '-10').toDate();

  db.WePayCheckout.destroy([
    {wepay_checkout_id: null},
    {state: null},
    {created_at: {lt: time}}
  ])
    .then(function (count) {
      console.log('Deleted ' + count + ' abandoned checkouts');
    })
    .catch(function (err) {
      console.error(err);
    });
}
