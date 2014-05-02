// Information about a secured item lent to a member.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('security', {
    memberId: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    paymentId: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    item: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    refundedAt: {
      type: DataTypes.DATE,
      allowNull: true
    },
    notes: DataTypes.TEXT
  });
}