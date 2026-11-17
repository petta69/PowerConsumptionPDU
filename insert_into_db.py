import sys
import mysql.connector
from datetime import datetime, timezone
import random
import time
from snmp import Engine, SNMPv1
import matplotlib.pyplot as plt
import numpy as np

import minimalmodbus
import serial


## Create user
# CREATE USER 'sony'@'localhost' IDENTIFIED BY 'Sony123456';
# GRANT ALL PRIVILEGES ON *.* TO 'sony'@'localhost';


## Create the Power table
# create table Power (id int AUTO_INCREMENT NOT NULL PRIMARY KEY, outlet_no int NOT NULL, event_time DATETIME NOT NULL, value VARCHAR(255) NOT NULL);

## PZEM
# Initialize the instrument (Port: /dev/ttyUSB0, Default Slave Address: 1)
pzem0 = minimalmodbus.Instrument('/dev/ttyUSB0', 1)

# Configure serial settings required by PZEM-004T v3.0
pzem0.serial.baudrate = 9600
pzem0.serial.bytesize = 8
pzem0.serial.parity = serial.PARITY_NONE
pzem0.serial.stopbits = 1
pzem0.serial.timeout = 0.5
pzem0.mode = minimalmodbus.MODE_RTU


def delete_old_data(num_hour=12):
    try:
        # 1. Establish the connection
        conn = mysql.connector.connect(
            host="localhost",
            user="sony",
            password="Sony123456",
            database="PowerConsumption"
        )
        cursor = conn.cursor()

        # 2. Execute a parameterized query (prevents SQL injection)
        query = "delete from Power where event_time < NOW() - INTERVAL %s HOUR"
        cursor.execute(query, (num_hour,))


    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return f"Error: {err}"

    finally:
        # 4. Clean up resources
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
        return f"Success: Deleted records older than {num_hour} hours"


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


def snmp_get_data():
    # Initialize the SNMP engine for version 1
    engine = Engine(SNMPv1)

    # Create a Manager pointing to the target IP and community string
    pdu = engine.Manager("192.168.197.12", community=b"public")

    # Send an SNMPv1 GET request for system description and location OIDs
    #response = pdu.get("1.3.6.1.4.1.21317.1.3.2.3.2.1.4", "1.3.6.1.4.1.21317.1.3.2.3.2.1.4.1")
    response = pdu.get("1.3.6.1.4.1.21317")
    print(response)


def get_pzem0_data():
    try:
        # Read 10 input registers starting at address 0x0000 (Function code 4)
        data = pzem0.read_registers(0, 10, functioncode=4)

        voltage = data[0] / 10.0                                # Volts (V)
        current = ((data[2] << 16) + data[1]) / 1000.0          # Amperes (A)
        power = ((data[4] << 16) + data[3]) / 10.0              # Watts (W)
        energy = ((data[6] << 16) + data[5])                    # Watt-hours (Wh)
        frequency = data[7] / 10.0                              # Hertz (Hz)
        power_factor = data[8] / 100.0                          # Power Factor (PF)
        alarm = data[9]                                         # 0xFFFF = Alarm, 0x0000 = OK

        print(f"Voltage:      {voltage} V")
        print(f"Current:      {current} A")
        print(f"Power:        {power} W")
        print(f"Energy:       {energy} Wh")
        print(f"Frequency:    {frequency} Hz")
        print(f"Power Factor: {power_factor}")

        return power
    
    except Exception as e:
        print(f"Error reading from PZEM: {e}")
        return None

def main():
    while True:
        ## Start by deleting old data (older than 12 hours)
        delete_old_data(num_hour=12)


        ## Create fake data and ingest
#        iso_utc_now = datetime.now(timezone.utc).isoformat()
        iso_utc_now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        event_time = iso_utc_now

        outlet_no = random.randint(0, 1)
        #value = random.randint(50, 230)
        value2 = random.randint(50, 230)

        value = get_pzem0_data()

        insert_data(0, event_time, value)
        insert_data(1, event_time, value2)

        time.sleep(2)  # Sleep for 5 seconds before inserting the next record


if __name__ == "__main__":
    main()
    sys.exit(0)