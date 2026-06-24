# models.py
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey, String, Integer, DateTime, Numeric, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Publisher(Base):
    __tablename__ = "publisher"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    books: Mapped[list["Book"]] = relationship(back_populates="publisher")


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publisher.id"), nullable=False)

    publisher: Mapped["Publisher"] = relationship(back_populates="books")
    stocks: Mapped[list["Stock"]] = relationship(back_populates="book")


class Shop(Base):
    __tablename__ = "shop"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    stocks: Mapped[list["Stock"]] = relationship(back_populates="shop")


class Stock(Base):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), nullable=False)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shop.id"), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    book: Mapped["Book"] = relationship(back_populates="stocks")
    shop: Mapped["Shop"] = relationship(back_populates="stocks")
    sales: Mapped[list["Sale"]] = relationship(back_populates="stock")


class Sale(Base):
    __tablename__ = "sale"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock.id"), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date_sale: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    stock: Mapped["Stock"] = relationship(back_populates="sales")


def create_tables(engine):
    Base.metadata.create_all(engine)

    from sqlalchemy import select
    from sqlalchemy.orm import Session

    def get_sales_by_publisher(session: Session, publisher_value):
        query = (
            select(Book.title, Shop.name, Sale.price, Sale.date_sale)
            .join(Book, Book.id == Stock.book_id)
            .join(Publisher, Publisher.id == Book.publisher_id)
            .join(Shop, Shop.id == Stock.shop_id)
            .join(Sale, Sale.stock_id == Stock.id)
        )

        if isinstance(publisher_value, int) or str(publisher_value).isdigit():
            query = query.where(Publisher.id == int(publisher_value))
        else:
            query = query.where(Publisher.name == publisher_value)

        query = query.order_by(Sale.date_sale.desc())

        return session.execute(query).all()