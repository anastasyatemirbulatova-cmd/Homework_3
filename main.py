# main.py
from models import Publisher, Book, Shop, Stock, Sale, create_tables
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Publisher, Book, Shop, Stock, Sale, create_tables
from queries import get_sales_by_publisher

DSN = os.getenv("DSN", "postgresql+psycopg2://user:password@localhost:5432/dbname")

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    create_tables(engine)
    with Session() as session:
        value = input("Введите имя или id издателя: ").strip()
        if value.isdigit():
            value = int(value)

        rows = get_sales_by_publisher(session, value)

        for title, shop_name, price, dt in rows:
            print(f"{title} | {shop_name} | {int(price) if float(price).is_integer() else price} | {dt:%d-%m-%Y}")