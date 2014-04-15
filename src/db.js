var Q = require('q');
var Sequelize = require('sequelize');

var config = require('../config/config');

var sequelize = new Sequelize(config.db.name, config.db.username, config.db.password, {
  dialect: config.db.dialect,
  host: config.db.host,
  port: config.db.port,
  pool: config.db.pool,

  define: {
    underscored: true,
    charset: 'utf8',
    timestamps: true
  }
})

var Member = sequelize.import('./models/member');
var Payment = sequelize.import('./models/payment');
var Dues = sequelize.import('./models/dues');
var Security = sequelize.import('./models/security');
var Donation = sequelize.import('./models/donation');
var WePayCheckout = sequelize.import('./models/wePayCheckout');

// Some payments are for dues (and linked to a member)
Member.hasMany(Dues);
Payment.hasMany(Dues);

// Some payments are security deposits (and linked to a member)
Member.hasMany(Security);
Payment.hasMany(Security);

// Some payments are donations
Payment.hasMany(Donation);

/**
 * Hack to add indexes until Sequelize gets support for them in models.
 * @returns a promise that resolves when the index is created
 */
function createIndexIfNotExists(table, attributes, options) {
  var qi = sequelize.getQueryInterface();
  return qi.showIndex(table)
    .then(function (indexes) {
      // See if it exists
      var exists = false;
      indexes.forEach(function (index) {
        if (index.name === options.indexName) {
          exists = true;
        }
      });

      // Not found, create it
      if (!exists) {
        return qi.addIndex(table, attributes, options);
      }

      return new Q();
    });
}

/**
 * @returns a promise that resolves when the database schema is synchronized to our models
 */
function sync() {
  return sequelize.sync({force: false})
    .then(function () {
      return createIndexIfNotExists('payments', ['method'], { indexName: 'payments_method_idx' });
    })
    .then(function () {
      return createIndexIfNotExists('payments', ['reference'], { indexName: 'payments_reference_idx' });
    });
}

module.exports = {
  sync: sync,
  sequelize: sequelize,

  // Models we loaded
  Member: Member,
  Payment: Payment,
  Dues: Dues,
  Security: Security,
  Donation: Donation,
  WePayCheckout: WePayCheckout
};