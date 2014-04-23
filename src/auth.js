var bcrypt = require('bcrypt');
var LocalStrategy = require('passport-local').Strategy;
var Q = require('q');

var rounds = 10;

/**
 * Hashes a password.
 *
 * @param plaintext the plaintext to hash
 * @returns a promise that resolves to the hash
 */
exports.hashPassword = function (plaintext) {
  var deferred = Q.defer();
  bcrypt.genSalt(rounds, function (err, salt) {
    bcrypt.hash(plaintext, salt, function (err, hash) {
      if (err) {
        deferred.reject(err);
      } else {
        deferred.resolve(hash);
      }
    });
  });
  return deferred.promise;
}

/**
 * Checks if the result of hashing the specified plaintext matches the specified hash.
 *
 * @param plaintext the plaintext to hash
 * @param hash the hash to check against
 * @returns a promise that resolves to true or false
 */
exports.checkPassword = function (plaintext, hash) {
  var deferred = Q.defer();
  bcrypt.compare(plaintext, hash, function (err, res) {
    if (err) {
      deferred.reject(err);
    } else {
      deferred.resolve(res);
    }
  });
  return deferred.promise;
}

/**
 * Configures Passport to use local authentication.
 */
exports.configurePassport = function (passport, db) {
  passport.use(new LocalStrategy({
      usernameField: 'email',
      passwordField: 'password'
    },
    function (email, password, done) {
      db.Member.find({where: {email: email}})
        .then(function (member) {
          if (member && exports.checkPassword(password, member.password_hash)) {
            done(null, member);
          } else {
            done(null, false);
          }
        })
        .catch(function (err) {
          done(err);
        });
    }));
}
