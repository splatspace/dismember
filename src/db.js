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

// Import the models
var Member = sequelize.import('./models/member');
var Payment = sequelize.import('./models/payment');
var Dues = sequelize.import('./models/dues');
var Security = sequelize.import('./models/security');
var Donation = sequelize.import('./models/donation');
var WePayCheckout = sequelize.import('./models/wePayCheckout');
var Role = sequelize.import('./models/role');

function associate() {
  // Some payments are for dues (and linked to a member)
  Member.hasMany(Dues);
  Payment.hasMany(Dues);

  // Some payments are security deposits (and linked to a member)
  Member.hasMany(Security);
  Payment.hasMany(Security);

  // Some payments are donations
  Payment.hasMany(Donation);

  // Members can belong to many roles
  Role.hasMany(Member, {through: 'members_roles'});
  Member.hasMany(Role, {through: 'members_roles'});
}

module.exports = {
  sequelize: sequelize,

  /**
   * @returns a promise that resolves when all database migrations have run
   */
  migrate: function() {
    var migrator = sequelize.getMigrator({
      path: process.cwd() + '/migrations'
    });

    // Set the model associations after migration so Sequelize doesn't create the join tables
    return migrator.migrate()
      .then(associate);
  },

  // Models we loaded
  Member: Member,
  Payment: Payment,
  Dues: Dues,
  Security: Security,
  Donation: Donation,
  WePayCheckout: WePayCheckout,
  Role: Role
};