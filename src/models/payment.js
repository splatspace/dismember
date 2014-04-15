var Q = require('q');

// A monetary payment made to the organization.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('payment', {
    amount: {
      type: DataTypes.DECIMAL(10, 2),
      min: 0,
      allowNull: false
    },
    method: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        isIn: [
          ['wepay', 'cash', 'check', 'goods']
        ]
      }
    },
    reference: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    notes: DataTypes.TEXT
  }, {
    underscored: true
  });
}