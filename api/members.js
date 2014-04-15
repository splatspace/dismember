var db = require('../src/db');

exports.create = function (req, res) {
  var member = req.body;
  db.Member.create(member)
    .success(function (member) {
      if (member) {
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
    .failure(function (err) {
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
      res.status(200).send(members);
    })
    .failure(function (err) {
      res.status(500).send();
    });
}