// Information about dues paid by a member.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('dues', {
    memberId: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    paymentId: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    periodStart: {
      type: DataTypes.DATE,
      allowNull: false
    },
    periodEnd: {
      type: DataTypes.DATE,
      allowNull: false
    },
    notes: DataTypes.TEXT
  });
}