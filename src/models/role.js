var auth = require('../auth');

// A system access role (admin, service, etc.)

module.exports = function (sequelize, DataTypes) {
  return sequelize.define('role', {
    name: {
      type: DataTypes.TEXT,
      allowNull: false,
      unique: true,
      validate: {
        notEmpty: true
      }
    }
  });
}