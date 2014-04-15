var Q = require('q');
var schedule = require('node-schedule');

var config = require('../config/config');

/**
 * @returns a promise that schedules background jobs
 */
exports.schedule = Q.fcall(function() {
  // Supports cron strings like:
  //   minute hour date month day_of_week [year]

  // Delete abandoned checkouts a few times a day
  schedule.scheduleJob('0 0,6,12,18 * * *', require('./jobs/cleanWePayCheckouts').run);

  // Refresh checkouts we may have missed IPNs for; once a day is enough
  schedule.scheduleJob('0 0 * * *', require('./jobs/refreshWePayCheckouts').run);
});
