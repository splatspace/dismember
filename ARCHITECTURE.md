# Application

Dismember is a straight-forward Flask web application.  Flask binds to the configured
TCP port and HTTP requests are routed to views based on their declared URI routes.
The SQLAlchemy ORM provides quick, high-level access to the database and views
generally query the models they need before rendering a page template.

## Blueprints

Flask provides the blueprint feature to organize related code and resources so they're
reusable within an application (and in other applications).  Some features are
used as blueprints in Dismember:

- crud (simple automated create/read/update/delete views for models)
- admin (provides administration features; uses crud)
- user (provides user features)

## Internal Services

When complex business rules apply (for example, when calculating if a past membership
period should be considered unpaid after a partial refund of that month's payment)
dedicated internal services can help.  These services live in modules at the top level
of the source tree named after the type of service.  For example, the dismember/dues.py
file contains the DuesService class with methods to calculate paid and unpaid dues.

## Routes

Views are organized in the source tree according to the type of service they provide.
Move views live inside blueprints, but a few general views can be found at the top-level
views directory dismember/views.  Use url_for() to link into views (see the Flask docs).

# Database

Dismember uses a relational database to store all its information.  SQLAlchemy's
object-releational mapper (ORM) provides an object-oriented abstraction over this
data, mapping database relations to Python object relations.

All the database relations (tables, types, views, sequences, etc.) this system uses
are defined in Python code in the dismember/models directory.  SQLAlchemy examines
the model classes when the application starts and queries the database schema
to make sure the classes are compatible with the database.  If the database doesn't
match, an error is raised and the application doesn't start.  Read the excellent
SQLAlchemy ORM documentation for more information.

# Models and Inheritance

Dismember uses SQLAlchemy's Joined Table Inheritance feature for some models.
This lets us express Python's class inheritance relationships inside the database
as related tables.  A foreign key points "up" from the derived class's table to the
parent class's table, and a not-null constraint ensures the "is-a" criteria are
met (you can't create a row in the child table without a row in the parent table that
satisfies all the parent table's constraints).  This sounds complicated, but
SQLAlchemy takes care of it all: simply use the child models as you would any model.

## Payments

There are different types of payments (dues, donations), and different ways to
make them (cash, check, WePay), different currencies (US dollars, Bitcoin), and
all kinds of states they may be in (check bounced, refunded, partially refunded,
charged back).  Here's a graph of inheritance of the payment classes in Dismember:

- Payment
  - DonationPayment
    - WePayDonationPayment
  - DuesPayment
    - WePayDuesPayment
    - ManualDuesPayment

The top-level Payment class is essentially a virtual class that defines a few things
all payments must be, but knows nothing about what kind of thing was paid for or
how it was paid.  It declares some properties that are useful for displaying
payments, but you'll have to use a subclass if you want to create a new payment.

Classes that directly subclass Payment define what the payment is for (donations,
dues, etc.).  These classes might have relationships to other models.  For
example, a dues payment links to one or more dues periods that the payment covers.
Most of these are also virtual classes, because they don't store information about
how the payment was made.  Go one more step down the inheritance hierarchy for the
concrete classes that define the payment method details.