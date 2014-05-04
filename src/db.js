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
  Dues.belongsTo(Payment);

  // Some payments are security deposits (and linked to a member)
  Member.hasMany(Security);
  Payment.hasMany(Security);
  Security.belongsTo(Payment);

  // Some payments are donations
  Member.hasMany(Donation);
  Payment.hasMany(Donation);
  Donation.belongsTo(Payment);

  // Members can belong to many roles
  Role.hasMany(Member, {through: 'members_roles'});
  Member.hasMany(Role, {through: 'members_roles'});
}

function createDefaultRoles() {
  return Role.findOrCreate({name: 'admin'})
    .then(Role.findOrCreate({name: 'board'}));
}

function createAdminMember() {
  var adminEmail = config.adminEmail;
  var adminPassword = config.adminPassword;

  return Role.find({where: {name: 'admin'}})
    .success(function (adminRole) {
      if (adminRole) {
        return Member.find({where: { email: adminEmail } })
          .success(function (member) {
            if (!member) {
              var adminAttrs = {
                email: adminEmail,
                membership_type: 'full',
                membership_status: 'active',
                name: 'Dismember Administrator',
                address: '123 Sesame Street',
                emergency_contact_name: 'Big Bird',
                emergency_contact_address: '123 Sesame Street',
                emergency_contact_phone: '+19195551212'
              };

              var adminMember = Member.build(adminAttrs);
              adminMember.validate();
              return adminMember.setPassword(adminPassword)
                .then(function () {
                  return adminMember.save();
                })
                .then(function () {
                  return adminMember.setRoles([adminRole]);
                });
            }
          });
      }
    });
}

module.exports = {
  sequelize: sequelize,

  /**
   * @returns a promise that resolves when all database migrations have run
   */
  migrate: function () {
    var migrator = sequelize.getMigrator({
      path: process.cwd() + '/migrations'
    });

    // Set the model associations after migration so Sequelize doesn't create the join tables
    return migrator.migrate()
      .then(associate);
  },

  /**
   * @returns a promise that resolves after default users and roles are created
   */
  createDefaults: function () {
    return Q.all([createDefaultRoles(), createAdminMember()]);
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