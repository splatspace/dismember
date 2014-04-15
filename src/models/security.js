// Information about a secured item lent to a member.

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('security', {
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
    item: {
      type: DataTypes.TEXT,
      allowNull: false,
      validate: {
        notEmpty: true
      }
    },
    refunded_at: {
      type: DataTypes.DATE,
      allowNull: true
    },
    notes: DataTypes.TEXT
  }, {
    underscored: true
  });
}