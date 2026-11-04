import mysql.connector
from datetime import datetime, timezone
import random
import time
from snmp import Engine, SNMPv1

## Create user
# CREATE USER 'sony'@'localhost' IDENTIFIED BY 'Sony123456';
# GRANT ALL PRIVILEGES ON *.* TO 'sony'@'localhost';


## Create the Power table
# create table Power (id int AUTO_INCREMENT NOT NULL PRIMARY KEY, outlet_no int NOT NULL, event_time DATETIME NOT NULL, value VARCHAR(255) NOT NULL);



def insert_data(outlet_no, event_time, value):
    """
    Inserts a new record into the Power table.
    
    :param outlet_no: The outlet number (int)
    :param event_time: The event time (datetime)
    :param value: The value associated with the event (str)
    """
    # 1. Establish the database connection
    connection = mysql.connector.connect(
        host="localhost",
        user="sony",
        password="Sony123456",
        database="PowerConsumption"
    )
    try:
        # 2. Create a cursor object
        cursor = connection.cursor()

        # 3. Define the parameterized SQL query
        insert_query = """
        INSERT INTO Power (outlet_no, event_time, value) 
        VALUES (%s, %s, %s)
        """
        
        # 4. Define the data as a tuple matching the placeholders
        power_data = (outlet_no, event_time, value)

        # 5. Execute the query
        cursor.execute(insert_query, power_data)

        # 6. Commit the transaction to save changes permanently
        connection.commit()

        # Optional: Get the total rows affected and the auto-incremented ID
        print(f"{cursor.rowcount} record successfully inserted.")
        print(f"Inserted Record ID: {cursor.lastrowid}")

    except mysql.connector.Error as error:
        print(f"Failed to insert record into MySQL table: {error}")

    finally:
        # 7. Always clean up and close your connections
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")


def get_data():
    # Initialize the SNMP engine for version 1
    engine = Engine(SNMPv1)

    # Create a Manager pointing to the target IP and community string
    localhost = engine.Manager("127.0.0.1", community=b"public")

    # Send an SNMPv1 GET request for system description and location OIDs
    response = localhost.get("1.3.6.1.4.1.21317.1.3.2.3.2.1.4", "1.3.6.1.4.1.21317.1.3.2.3.2.1.4.1")
    print(response)


if __name__ == "__main__":
    while True:

        iso_utc_now = datetime.now(timezone.utc).isoformat()
        event_time = iso_utc_now

        outlet_no = random.randint(0, 1)
        value = random.randint(50, 230)
        value2 = random.randint(50, 230)

        insert_data(0, event_time, value)
        insert_data(1, event_time, value2)

        time.sleep(5)  # Sleep for 5 seconds before inserting the next record

