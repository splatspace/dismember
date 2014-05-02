// A WePay checkout (the thing that gives us money) either in-progress
// or completed.  HTTP callbacks from WePay inform us of changes in state
// as they happen.
//
//   https://www.wepay.com/developer/reference/checkout#create
//
// Not all checkout object fields are modeled here, just the ones we
// think we'll need.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('wepay_checkouts', {

    // Allow UUIDs as primary keys so we can pass them through redirects with a low
    // chance of someone guessing another checkout ID to continue with.

    id: {
      type: DataTypes.TEXT,
      primaryKey: true,
      allowNull: false
    },

    // Our internal values

    purpose: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        isIn: [
          ['donation', 'dues', 'security']
        ]
      }
    },

    // Required for create

    accountId: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    shortDescription: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    type: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        isIn: [
          ['GOODS', 'SERVICE', 'DONATION', 'EVENT', 'PERSONAL']
        ]
      }
    },
    amount: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },

    // Optional for create

    currency: DataTypes.TEXT,
    longDescription: DataTypes.TEXT,
    payerEmailMessage: DataTypes.TEXT,
    payeeEmailMessage: DataTypes.TEXT,
    referenceId: DataTypes.TEXT,
    appFee: DataTypes.DECIMAL(10, 2),
    feePayer: {
      type: DataTypes.TEXT,
      validate: {
        isIn: [
          ['payer', 'payee']
        ]
      }
    },
    redirectUri: DataTypes.TEXT,
    callbackUri: DataTypes.TEXT,
    autoCapture: DataTypes.BOOLEAN,

    // Updated from IPNs
    wepayCheckoutId: DataTypes.INTEGER,
    payerName: DataTypes.TEXT,
    payerEmail: DataTypes.TEXT,
    state: DataTypes.TEXT,
    gross: DataTypes.DECIMAL(10, 2),
    fee: DataTypes.DECIMAL(10, 2),
    amountRefunded: {
      type: DataTypes.DECIMAL(10, 2)
    },
    amountChargedBack: {
      type: DataTypes.DECIMAL(10, 2)
    }
  }, {
    instanceMethods: {
      // Converts this object's values to an object for submission to the WePay web services
      toWebValues: function () {
        return {
          account_id: this.accountId,
          short_description: this.shortDescription,
          type: this.type,
          amount: this.amount,
          currency: this.currency,
          long_description: this.longDescription,
          payer_email_message: this.payerEmailMessage,
          payee_email_message: this.payeeEmailMessage,
          reference_id: this.referenceId,
          app_fee: this.appFee,
          fee_payer: this.feePayer,
          redirect_uri: this.redirectUri,
          callback_uri: this.callbackUri,
          auto_capture: this.autoCapture
        }
      }
    }
  });
}