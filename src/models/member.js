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
    membership_type: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        isIn: [
          ['associate', 'full']
        ]
      }
    },
    membership_status: {
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
    emergency_contact_name: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    emergency_contact_address: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    emergency_contact_phone: {
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