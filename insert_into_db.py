import sys
import mysql.connector
from datetime import datetime, timezone
import random
import time
from snmp import Engine, SNMPv1
import matplotlib.pyplot as plt
import numpy as np

## Create user
# CREATE USER 'sony'@'localhost' IDENTIFIED BY 'Sony123456';
# GRANT ALL PRIVILEGES ON *.* TO 'sony'@'localhost';


## Create the Power table
# create table Power (id int AUTO_INCREMENT NOT NULL PRIMARY KEY, outlet_no int NOT NULL, event_time DATETIME NOT NULL, value VARCHAR(255) NOT NULL);

def get_data(no_events=100):
    np_data = np.empty((0, 3))
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
        query = "SELECT event_time, value, outlet_no FROM Power ORDER BY event_time DESC LIMIT %s"
        cursor.execute(query, (no_events,))

        # 3. Fetch and display the results
        for row in cursor.fetchall():
            event_time = row[0].strftime('%H:%M:%S') 
            np_data = np.append(np_data, [[event_time, row[2], float(row[1])]], axis=0)

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        # 4. Clean up resources
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
        return np_data


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


def create_double_line_chart(data):
    plt.style.use('dark_background')

    # plot
    fig, ax = plt.subplots()

    ax.invert_xaxis()

    ## Prepp arrays
    x_data = []
    np_data_0 = np.empty((0, 1))
    np_data_1 = np.empty((0, 1))

    ## Excract data and append to arrays
    for i in range(data.shape[0]):
        if data[i,1] == '0':
            np_data_0 = np.append(np_data_0, [[float(data[i,2])]], axis=0)
            x_data.append(data[i,0])
        elif data[i,1] == '1':
            np_data_1 = np.append(np_data_1, [[float(data[i,2])]], axis=0)

    ## Plot data
    ax.plot(x_data, np_data_0[:,0], color='red', linewidth=2, label='55BZ40L')
    ax.plot(x_data, np_data_1[:,0], color='yellow', linewidth=2, label='55BZ40P')
#    ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True)
    # ax.legend(
    #     bbox_to_anchor=(0.0, 0.0, 1.0, 1.0), # Static container bounds
    #     loc="upper left",                    # Traps text inside container corner
    #     frameon=True,                        # Draws background frame
    #     facecolor='#1c1c1c',                 # Dark theme friendly box color
    #     edgecolor='gray',                    # Clean borders
    #     framealpha=1.0                       # 100% opaque block over passing data
    # )
    

    #ax.yaxis.set_label_coords(-0.15, 0.5)

    ## Set axis limits and ticks
    ax.set(xlim=(-1, len(x_data)), xticks=np.arange(0, len(x_data), len(x_data)//5),
        ylim=(min(np_data_0[:,0].min(), np_data_1[:,0].min())-10, max(np_data_0[:,0].max(), np_data_1[:,0].max())+10),
        yticks=np.arange(min(np_data_0[:,0].min(), np_data_1[:,0].min()), max(np_data_0[:,0].max(), np_data_1[:,0].max()), 20))
    ax.axhline(np.mean(np.concatenate([np_data_0[:,0], np_data_1[:,0]])), color='gray', linestyle='--', linewidth=1)

    ## Calc accumulated data for each outlet
    acc_data_0 = np.sum(np_data_0[:,0])
    acc_data_1 = np.sum(np_data_1[:,0])

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in upper left in axes coords
    ax.text(0.05, -0.15, f'Accumulated: Outlet 0 = {acc_data_0}, Outlet 1 = {acc_data_1}', transform=ax.transAxes, fontsize=10,
            verticalalignment='center', bbox=props)

    ## Reverse X axis to make sure latest value is on the right side of the chart
    #ax.set_xinverted(True)
    

    ax.set_title("Power Consumption (W)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Power (W)")

    ax.legend(
        loc="baseline",                    # Aligns the text baseline perfectly with the title text
        bbox_to_anchor=(0.13, 0.92),       # Absolute canvas coordinates (X=0.13 is the left margin line)
        bbox_transform=fig.transFigure,    # Bypasses axes shifts completely
        ncol=2,                            # Places labels horizontally side-by-side to save vertical space
        frameon=True,                      
        facecolor='#1c1c1c',               
        edgecolor='none',                  # Strips the border box away for a clean top-bar look
        framealpha=1.0                     
    )

    #plt.show()
    plt.savefig(f'static/powerchart.png', dpi=200, bbox_inches='tight')
    print(f"DEBUG: Chart saved to static/powerchart.png with accumulated values: Outlet 0 = {acc_data_0}, Outlet 1 = {acc_data_1}")
    plt.close(fig)  # Close the figure to free up memory


def snmp_get_data():
    # Initialize the SNMP engine for version 1
    engine = Engine(SNMPv1)

    # Create a Manager pointing to the target IP and community string
    localhost = engine.Manager("127.0.0.1", community=b"public")

    # Send an SNMPv1 GET request for system description and location OIDs
    response = localhost.get("1.3.6.1.4.1.21317.1.3.2.3.2.1.4", "1.3.6.1.4.1.21317.1.3.2.3.2.1.4.1")
    print(response)



def main():
    while True:
        ## Create fake data and ingest
#        iso_utc_now = datetime.now(timezone.utc).isoformat()
        iso_utc_now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        event_time = iso_utc_now

        outlet_no = random.randint(0, 1)
        value = random.randint(50, 230)
        value2 = random.randint(50, 230)

        insert_data(0, event_time, value)
        insert_data(1, event_time, value2)


        ## Create chart    
        data = get_data(no_events=50)
        create_double_line_chart(data)

        time.sleep(5)  # Sleep for 5 seconds before inserting the next record


if __name__ == "__main__":
    main()
    sys.exit(0)