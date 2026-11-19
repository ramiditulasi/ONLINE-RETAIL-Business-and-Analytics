import getpass
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

password = getpass.getpass("MySQL root password: ")
encoded_password = quote_plus(password)

engine = create_engine(
    f"mysql+mysqlconnector://root:{encoded_password}"
    "@localhost/online_retail",
    pool_pre_ping=True
)

with engine.connect() as connection:
    row_count = connection.execute(
        text("SELECT COUNT(*) FROM raw_invoice_lines")
    ).scalar_one()

    customer_count = connection.execute(
        text("SELECT COUNT(*) FROM customer_rfm")
    ).scalar_one()

    print("MySQL connection successful!")
    print("Retail records:", row_count)
    print("RFM customers:", customer_count)

