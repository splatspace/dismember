// Information about dues paid by a member.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('dues', {
    member_id: {
      type: DataTypes.INTEGER,
      references: 'members',
      referencesKey: 'id',
      allowNull: false
    },
    payment_id: {
      type: DataTypes.INTEGER,
      references: 'payments',
      referencesKey: 'id',
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