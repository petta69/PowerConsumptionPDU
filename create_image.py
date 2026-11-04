import sys
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

def create_double_line_chart(data):
    plt.style.use('dark_background')

    # plot
    fig, ax = plt.subplots()

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

    ## Set axis limits and ticks
    ax.set(xlim=(-1, len(x_data)), xticks=np.arange(0, len(x_data), len(x_data)/5),
        ylim=(min(np_data_0[:,0].min(), np_data_1[:,0].min())-10, max(np_data_0[:,0].max(), np_data_1[:,0].max())+10),
        yticks=np.arange(min(np_data_0[:,0].min(), np_data_1[:,0].min()), max(np_data_0[:,0].max(), np_data_1[:,0].max()), 20))
    ax.axhline(np.mean(np.concatenate([np_data_0[:,0], np_data_1[:,0]])), color='gray', linestyle='--', linewidth=1)

    ## Reverse X axis to make sure latest value is on the right side of the chart
    ax.set_xinverted(True)

    ax.set_title("Power Consumption (W)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Power (W)")
    ax.legend()

    #plt.show()
    plt.savefig(f'static/powerchart.png', dpi=200, bbox_inches='tight')



def main():
    data = get_data(no_events=50)
    create_double_line_chart(data)



if __name__ == "__main__":
    main()
    print("Image created successfully.")
    sys.exit(0)
