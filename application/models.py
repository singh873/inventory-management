from .database import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), default="user", nullable=False)

    requests = db.relationship("Request", backref="user", )


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    prod_name = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="available", nullable=False)

    requests = db.relationship("Request", backref="product",)


class Request(db.Model):
    __tablename__ = "request"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    prod_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    units_requested=db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="requested", nullable=False)
