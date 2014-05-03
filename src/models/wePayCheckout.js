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

    account_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    short_description: {
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
    long_description: DataTypes.TEXT,
    payer_email_message: DataTypes.TEXT,
    payee_email_message: DataTypes.TEXT,
    reference_id: DataTypes.TEXT,
    app_fee: DataTypes.DECIMAL(10, 2),
    fee_payer: {
      type: DataTypes.TEXT,
      validate: {
        isIn: [
          ['payer', 'payee']
        ]
      }
    },
    redirect_uri: DataTypes.TEXT,
    callback_uri: DataTypes.TEXT,
    auto_capture: DataTypes.BOOLEAN,

    // Updated from IPNs
    wepay_checkout_id: DataTypes.INTEGER,
    payer_name: DataTypes.TEXT,
    payer_email: DataTypes.TEXT,
    state: DataTypes.TEXT,
    gross: DataTypes.DECIMAL(10, 2),
    fee: DataTypes.DECIMAL(10, 2),
    amount_refunded: {
      type: DataTypes.DECIMAL(10, 2)
    },
    amount_charged_back: {
      type: DataTypes.DECIMAL(10, 2)
    }
  });
}