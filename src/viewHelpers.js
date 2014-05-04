var moment = require('moment');
var config = require('../config/config');

module.exports = {
  register: function (locals) {
    locals.uriPathPrefix = config.uriPathPrefix;

    /**
     * Capitalizes the first letter in the specified string.
     */
    locals.ucfirst = function (value) {
      return value.charAt(0).toUpperCase() + value.slice(1);
    };

    locals.toShortDateString = function (date) {
      if (!date) {
        return '';
      }
      return moment(date).format('YYYY-MM-DD');
    }
  }
}
