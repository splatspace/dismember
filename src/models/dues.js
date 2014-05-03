// Information about dues paid by a member.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('dues', {
    member_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    payment_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    period_start: {
      type: DataTypes.DATE,
      allowNull: false
    },
    period_end: {
      type: DataTypes.DATE,
      allowNull: false
    },
    notes: DataTypes.TEXT
  });
}