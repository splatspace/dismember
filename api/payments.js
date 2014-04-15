var db = require('../src/db');

exports.create = function (req, res) {
  var payment = req.body;
  db.Payment.create(payment)
    .success(function (payment) {
      if (payment) {
        res
          .status(201)
          .set('Location', req.path + '/' + payment.id)
          .send(payment);
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

  db.Payment.find({where: where})
    .success(function (payment) {
      if (payment) {
        res.status(200).send(payment);
      } else {
        res.status(404).send();
      }
    })
    .failure(function (err) {
      res.status(500).send();
    });
}

exports.list = function (req, res) {
  db.Payment.findAll()
    .success(function (payments) {
      res.status(200).send(payments);
    })
    .failure(function (err) {
      res.status(500).send();
    });
}