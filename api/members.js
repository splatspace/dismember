var Q = require('q');
var db = require('../src/db');

exports.create = function (req, res) {
  var member = req.body;

  var dbMember = db.Member.build(member);

  // Manual validation pass because we need to hash the password
  var validation = dbMember.validate();
  if (validation) {
    res
      .status(403)
      .send(validation);
    return;
  }

  dbMember.setPassword(member.password)
    .then(function (hash) {
      return dbMember.save();
    })
    .then(function (member) {
      if (member) {
        member.hidePrivateProperties();
        res
          .status(201)
          .set('Location', req.path + '/' + member.id)
          .send(member);
      } else {
        res
          .status(404)
          .send();
      }
    })
    .catch(function (err) {
      res
        .status(403)
        .send(err);
    });
}

exports.get = function (req, res, id) {
  var where = {};
  if (parseInt(id)) {
    where.id = id;
  } else {
    where.email = id;
  }

  db.Member.find({where: where})
    .success(function (member) {
      if (member) {
        member.hidePrivateProperties();
        res.status(200).send(member);
      } else {
        res.status(404).send();
      }
    })
    .failure(function (err) {
      res.status(500).send();
    });
}

exports.list = function (req, res) {
  db.Member.findAll()
    .success(function (members) {
      members.forEach(function (member) {
        member.hidePrivateProperties();
      });
      res.status(200).send(members);
    })
    .failure(function (err) {
      res.status(500).send();
    });
}