// Information about a donation to the organization.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('donation', {
    payment_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    notes: DataTypes.TEXT
  });
}