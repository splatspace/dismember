var auth = require('../auth');

// A human member of the organization.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('member', {
    email: {
      type: DataTypes.TEXT,
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true
      }
    },
    password: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    membershipType: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        isIn: [
          ['associate', 'full']
        ]
      }
    },
    membershipStatus: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        isIn: [
          ['application', 'active', 'suspended', 'terminated']
        ]
      }
    },
    name: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    address: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    phone: DataTypes.TEXT,
    emergencyContactName: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    emergencyContactAddress: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    emergencyContactPhone: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    notes: DataTypes.TEXT
  }, {
    instanceMethods: {
      /**
       * Tests if the specified role is configured on this member.
       *
       * @param role the name of the role to test
       * @returns a promise that resolves to true or false
       */
      roleEnabled: function(role) {
        return this.getRoles()
          .then(function(roles) {
            return roles.some(function (r) {
              return r.name === role;
            });
          })
          .catch(function (err) {
            return false;
          })
      },

      /**
       * Sets the password for a member.
       *
       * @param plaintext the plain text password to set
       * @returns a promise that resolves to the password hash that was set
       */
      setPassword: function (plaintext) {
        var that = this;
        return auth.hashPassword(plaintext)
          .then(function (hash) {
            that.setDataValue('password', hash);
          });
      },

      /**
       * Checks if a plaintext password matches this member's password hash.
       * @param plaintext the plaintext password to check
       * @returns a promise that resolves to true or false
       */
      verifyPassword: function (plaintext) {
        var hash = this.getDataValue('password');
        return auth.checkPassword(plaintext, hash);
      },

      hidePrivateProperties: function() {
        return this.setDataValue('password', undefined);
      }
    }
  });
}