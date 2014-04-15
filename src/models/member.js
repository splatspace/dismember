// A human member of the organization.

module.exports = function(sequelize, DataTypes) {
  return sequelize.define('member', {
    email: {
      type: DataTypes.TEXT,
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true
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
    underscored: true
  });
}