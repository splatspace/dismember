module.exports = {
  up: function (migration, DataTypes, done) {
    return createMembers(migration, DataTypes)
      .then(function () {
        return createRoles(migration, DataTypes);
      })
      .then(function () {
        return createMembersRoles(migration, DataTypes);
      })
      .then(function () {
        return createPayments(migration, DataTypes);
      })
      .then(function () {
        return createDues(migration, DataTypes);
      })
      .then(function () {
        return createSecurities(migration, DataTypes);
      })
      .then(function () {
        return createDonations(migration, DataTypes);
      })
      .then(function () {
        return createWePayCheckouts(migration, DataTypes);
      })
      .then(function() {
        done();
      });
  },

  down: function (migration, DataTypes, done) {
    done('not supported');
  }
}

function createWePayCheckouts(migration, DataTypes) {
  return migration.createTable('wepay_checkouts', {
    id: {
      type: DataTypes.TEXT,
      primaryKey: true,
      allowNull: false
    },
    purpose: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    account_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    short_description: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    type: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    amount: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },
    currency: DataTypes.TEXT,
    long_description: DataTypes.TEXT,
    payer_email_message: DataTypes.TEXT,
    payee_email_message: DataTypes.TEXT,
    reference_id: DataTypes.TEXT,
    app_fee: DataTypes.DECIMAL(10, 2),
    fee_payer: {
      type: DataTypes.TEXT
    },
    redirect_uri: DataTypes.TEXT,
    callback_uri: DataTypes.TEXT,
    auto_capture: DataTypes.BOOLEAN,
    wepay_checkout_id: DataTypes.INTEGER,
    payer_name: DataTypes.TEXT,
    payer_email: DataTypes.TEXT,
    state: DataTypes.TEXT,
    gross: DataTypes.DECIMAL(10, 2),
    fee: DataTypes.DECIMAL(10, 2),
    amount_refunded: {
      type: DataTypes.DECIMAL(10, 2)
    },
    amount_charged_back: {
      type: DataTypes.DECIMAL(10, 2)
    }
  });
}

function createDonations(migration, DataTypes) {
  return migration.createTable('donations', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    payment_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'payments',
      referencesKey: 'id'
    },
    notes: DataTypes.TEXT
  });
}

function createSecurities(migration, DataTypes) {
  return migration.createTable('securities', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    member_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'members',
      referencesKey: 'id'
    },
    payment_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'payments',
      referencesKey: 'id'
    },
    item: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    refunded_at: {
      type: DataTypes.DATE,
      allowNull: true
    },
    notes: DataTypes.TEXT
  });
}

function createDues(migration, DataTypes) {
  return migration.createTable('dues', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    member_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'members',
      referencesKey: 'id'
    },
    payment_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'payments',
      referencesKey: 'id'
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

function createPayments(migration, DataTypes) {
  return migration.createTable('payments', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    amount: {
      type: DataTypes.DECIMAL(10, 2),
      min: 0,
      allowNull: false
    },
    method: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    reference: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    notes: DataTypes.TEXT
  })
    .then(function () {
      return migration.addIndex('payments', ['method'], { indexName: 'payments_method_idx' });
    })
    .then(function () {
      return migration.addIndex('payments', ['reference'], { indexName: 'payments_reference_idx' });
    });
}

function createRoles(migration, DataTypes) {
  return migration.createTable('roles', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    created_at: {
      type: DataTypes.DATE,
      allowNull: false
    },
    updated_at: {
      type: DataTypes.DATE,
      allowNull: false
    },
    name: {
      type: DataTypes.TEXT,
      allowNull: false,
      unique: true
    }
  });
}

function createMembersRoles(migration, DataTypes) {
  return migration.createTable('members_roles', {
    // No ID for a join table
    created_at: {
      type: DataTypes.DATE,
      allowNull: false
    },
    updated_at: {
      type: DataTypes.DATE,
      allowNull: false
    },
    member_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'members',
      referencesKey: 'id'
    },
    role_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: 'roles',
      referencesKey: 'id'
    }
  });
}

function createMembers(migration, DataTypes) {
  return migration.createTable('members',
    {
      id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false
      },
      updated_at: {
        type: DataTypes.DATE,
        allowNull: false
      },
      email: {
        type: DataTypes.TEXT,
        allowNull: false,
        unique: true
      },
      password: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      membership_type: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      membership_status: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      name: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      address: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      phone: DataTypes.TEXT,
      emergency_contact_name: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      emergency_contact_address: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      emergency_contact_phone: {
        type: DataTypes.TEXT,
        allowNull: false
      },
      notes: DataTypes.TEXT
    }
  );
}