var uuid = require('node-uuid');
var _ = require('underscore');
var Q = require('q');

var db = require('./db');
var config = require('../config/config')
var wePayApi = require('./wePayApi');

/**
 * Returns a copy of the specified checkout object with only the properties allowed
 * by the WePay web service.
 */
function dbToApi(checkout) {
  return {
    account_id: checkout['account_id'],
    short_description: checkout['short_description'],
    type: checkout['type'],
    amount: checkout['amount'],
    currency: checkout['currency'],
    long_description: checkout['long_description'],
    reference_id: checkout['reference_id'],
    fee: {
      fee_payer: checkout['fee_payer'],
    },
    callback_uri: checkout['callback_uri'],
    auto_capture: checkout['auto_capture'],
    hosted_checkout: {
      mode: 'regular',
      funding_sources: ['credit_card', 'payment_bank']
    }
  };
}

/**
 * Invoked when a WePayCheckout has been refreshed from the server.
 *
 * @param checkout the new checkout
 * @param oldState the previous state
 */
function onCheckoutRefreshed(checkout, oldState) {
  if (checkout.state !== oldState) {
    // If the new state is one of these, the amount of money we now have has changed, so
    // we need to create or update the Payment object associated with the checkout.
    //
    // captured: the payment cleared; we can withdraw the money (create a payment)
    // refunded: we chose to refund some or all of the money (update a payment)
    // charged back: the customer took some or all of the money back (update a payment)
    switch (checkout.state) {
      case 'captured':
      case 'refunded':
      case 'charged back':
        createOrUpdatePayment(checkout);
        break;
    }
  }
}

/**
 * Create or update the Payment associated with the specified Checkout to have the
 * correct amount, as Checkouts may change over time (partial refunds, charge backs, etc.).
 *
 * @param checkout the latest checkout
 */
function createOrUpdatePayment(checkout) {
  // amount_refunded and amount_charged_back are a gross amounts (they include the refund
  // of the payer's service fee, if they paid it).
  var refundedNet = checkout.amount_refunded || 0;
  var chargedBackNet = checkout.amount_charged_back || 0;
  if (checkout.fee != null && checkout.fee.fee_payer === 'payer') {
    if (refundedNet > 0) {
      refundedNet = refundedNet - checkout.fee.processing_fee;
    }
    if (chargedBackNet > 0) {
      chargedBackNet = chargedBackNet - checkout.fee.processing_fee;
    }
  }

  var paymentAttrs =  {
    // Only one of refundedNet or chargedBackNet should ever be positive
    amount: checkout.amount - refundedNet - chargedBackNet,
    method: 'wepay',
    reference: checkout.id
  };

  db.Payment.findOrCreate(
    {
      method: 'wepay',
      reference: checkout.id
    }, paymentAttrs)
    .spread(function(payment, created) {
      if (created) {
        return payment;
      } else {
        // Update all the attributes
        return payment.updateAttributes(paymentAttrs);
      }
    })
    .catch(function(err) {
      console.error('Error creating or updating payment for checkout ' + checkout.id + ': ' + err);
    });
}

/**
 * Authorizes a new checkout.  This is the first step in the checkout process, in which
 * we ask the user to allow us to access his account for the purposes of collecting
 * payments.
 *
 * This function sets the id and reference_id properties of the checkout to a UUID
 * value, overwriting any previously set value.  This UUID will be the value of the "state" query
 * param when the user returns to the submitUri.
 *
 * @param {object} checkout a WePayCheckout model object
 * @param {string} submitUri the URI to send the user to (with some new query params) after they have authorized the checkout at WePay so we can submit it
 * @returns {promise} a promise that resolves to the URI the user should visit to authorize the checkout
 */
exports.authorizeCheckout = function (checkout, submitUri) {
  if (!checkout) {
    throw 'checkout is required';
  }
  if (checkout.id) {
    throw 'checkout already has an internal UUID';
  }
  if (!submitUri) {
    throw 'submitUri is required';
  }

  // We use id instead of uuid because that's what Sequelize wants for the primary key
  checkout.id = uuid.v4();
  checkout.reference_id = checkout.id;

  // Create it in the database and return the auth URL
  return db.WePayCheckout.create(checkout)
    .then(function (checkout) {
      return Q.fcall(wePayApi.getAuthorizeUrl, submitUri, 'collect_payments', checkout.id);
    });
}

/**
 * Submits an authorized checkout to WePay for processing.  This is the second step in the
 * checkout process.
 *
 * @param {string} checkoutUuid the UUID of the checkout that was previously authorized
 * @returns {promise} a promise that resolves to the URI to send the user to to confirm and complete the checkout
 */
exports.submitCheckout = function (checkoutUuid) {
  if (!checkoutUuid) {
    throw 'checkoutUuid is required';
  }

  return db.WePayCheckout.find(checkoutUuid)
    .then(function (checkout) {
      if (checkout) {
        // Convert the database object to the API object
        var checkoutValues = dbToApi(checkout.values);

        // Submit the checkout to WePay
        return wePayApi.call(config.wePayAccount.accessToken, '/checkout/create', checkoutValues)
          .then(function (checkoutResponse) {
            // Update the DB object with server-side WePay checkout ID
            checkout.wepay_checkout_id = checkoutResponse.checkout_id;
            return checkout.updateAttributes(checkout, ['wepay_checkout_id'])
              .then(function (checkout) {
                // Promise the confirmation URI
                return Q.fcall(function () {
                  return checkoutResponse.hosted_checkout.checkout_uri;
                });
              });
          });
      } else {
        throw 'Could not find an authorized checkout for UUID ' + checkoutUuid;
      }
    });
}

/**
 * Refreshes local information about a checkout from the WePay servers.  This method is
 * primarily for IPN handlers.
 *
 * @param {string} checkoutId the ID WePay assigned after the checkout was submitted; this is NOT the local checkout UUID
 * @returns a promise that resolves to the refreshed WePayCheckout
 */
exports.refreshCheckout = function (checkoutId) {
  if (!checkoutId) {
    throw 'checkoutId is required';
  }

  return wePayApi.call(config.wePayAccount.accessToken, '/checkout', {checkout_id: checkoutId})
    .then(function (checkoutResponse) {

      // Look it up by our UUID, which we stored in reference_id
      return db.WePayCheckout.find(checkoutResponse.reference_id)
        .then(function (checkout) {
          if (checkout) {
            // Save the old state for comparison purposes
            var oldState = checkout.state;

            // Update the database with new info about the checkout
            checkout.amount_refunded = checkoutResponse.refund.amount_refunded;
            checkout.amount_charged_back = checkoutResponse.chargeback.amount_charged_back;
            checkout.state = checkoutResponse.state;
            checkout.payer_name = checkoutResponse.payer.name;
            checkout.payer_email = checkoutResponse.payer.email;
            checkout.gross = checkoutResponse.gross;
            checkout.fee = checkoutResponse.fee.processing_fee;

            return checkout.updateAttributes(checkout, ['amount_refunded', 'amount_charged_back', 'state', 'payer_name', 'payer_email', 'gross', 'fee'])
              .then(function (checkout) {
                onCheckoutRefreshed(checkout, oldState);

                return Q.fcall(function () {
                  return checkout;
                });
              });
          } else {
            throw 'Could not find a checkout with UUID ' + checkoutResponse.reference_id;
          }
        });
    });
}
