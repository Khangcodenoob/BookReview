from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user", index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    orders = db.relationship("Order", back_populates="user", lazy="selectin")


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    slug = db.Column(db.String(255), unique=True, index=True)

    books = db.relationship("Book", back_populates="category", lazy="selectin")


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(512))
    genre = db.Column(db.String(100))
    publisher = db.Column(db.String(255))
    num_pages = db.Column(db.Integer)
    book_code = db.Column(db.String(100), unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), index=True)

    # E-commerce fields
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    isbn = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    category = db.relationship("Category", back_populates="books", lazy="joined")
    order_items = db.relationship("OrderItem", back_populates="book")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
        index=True,
    )
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("User", back_populates="orders", lazy="joined")
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    payments = db.relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)

    # Snapshot fields
    title_snapshot = db.Column(db.String(255), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")
    book = db.relationship("Book", back_populates="order_items", lazy="joined")


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False, default="cod")
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    paid_at = db.Column(db.DateTime)
    txn_ref = db.Column(db.String(100), unique=True)

    order = db.relationship("Order", back_populates="payments")

