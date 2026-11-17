import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import matplotlib.pyplot as plt
import numpy as np
import mysql.connector

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

# Path to your image on disk
IMAGE_PATH = os.path.abspath("static/powerchart.png")

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
    fig, ax = plt.subplots(figsize=(12, 4))

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

    ## Make sure we have enough data points to plot
    if len(x_data) < 25 or np_data_0.size == 0 or np_data_1.size == 0:
        print("DEBUG: Not enough data points to plot. Skipping chart creation.")
        return  

    ## Plot data
    bzl_plot, = ax.plot(x_data, np_data_0[:,0], color='red', linewidth=2, label='55BZ40L')
    bzp_plot, = ax.plot(x_data, np_data_1[:,0], color='yellow', linewidth=2, label='55BZ40P')

    ax.legend(handles=[bzl_plot, bzp_plot], loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, facecolor='#1c1c1c', edgecolor='gray', framealpha=1.0)
    
    ## Set axis limits and ticks
    ax.set(xlim=(-1, len(x_data)), xticks=np.arange(0, len(x_data), len(x_data)//5),
        ylim=(min(np_data_0[:,0].min(), np_data_1[:,0].min())-10, max(np_data_0[:,0].max(), np_data_1[:,0].max())+10),
        yticks=np.arange(min(np_data_0[:,0].min(), np_data_1[:,0].min()), max(np_data_0[:,0].max(), np_data_1[:,0].max()), 20))
    ax.axhline(np.mean(np.concatenate([np_data_0[:,0], np_data_1[:,0]])), color='gray', linestyle='--', linewidth=1)

    ## Calc accumulated data for each outlet
    acc_data_0 = np.sum(np_data_0[:,0]) / 1000
    acc_data_1 = np.sum(np_data_1[:,0]) / 1000

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in under graph in axes coords
    ax.text(0, -0.3, f'Accumulated: \n55BZ40L = {acc_data_0:.2f}kW\n55BZ40P = {acc_data_1:.2f}kW', 
            transform=ax.transAxes, 
            fontsize=10,
            verticalalignment='center',
            color='blue',
            bbox=dict(
                facecolor="yellow",   # Background fill color
                edgecolor="black",    # Border color (use "none" for no border)
                alpha=0.8,            # Background transparency (0 to 1)
                pad=5.0,              # Padding inside the box in points
                boxstyle="round,pad=0.5"  # Optional: rounded corners
                ),
            )

    ## Reverse X axis to make sure latest value is on the right side of the chart
    ax.set_xinverted(True)
    

    ax.set_title("Power Consumption (W)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Power (W)")

    #plt.show()
    plt.savefig(f'static/powerchart.png', dpi=200, bbox_inches='tight')
    print(f"DEBUG: Chart saved to static/powerchart.png with accumulated values: Outlet 0 = {acc_data_0:.1f}, Outlet 1 = {acc_data_1:.1f}")
    plt.close(fig)  # Close the figure to free up memory


def cache_bust(static_path) -> str:
    # FIX: Convert the Starlette URL object to a plain string first
    static_path_str = str(static_path)
    
    base_dir = os.path.abspath(".") 
    local_path = os.path.join(base_dir, static_path_str.lstrip("/"))
    
    if os.path.exists(local_path):
        mtime = int(os.path.getmtime(local_path))
        return f"{static_path_str}?v={mtime}"
    
    print(f"DEBUG: File not found at {local_path}") 
    return static_path_str

templates.env.filters["cache_bust"] = cache_bust

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

# NEW: Endpoint for JavaScript to poll
@app.get("/api/image-version")
async def get_image_version():
    ## Create chart    
    try:
        data = get_data(no_events=50)
        create_double_line_chart(data)
    except Exception as e:
        print(f"DEBUG: Error creating chart: {e}")

    if os.path.exists(IMAGE_PATH):
        mtime = int(os.path.getmtime(IMAGE_PATH))
        return JSONResponse({"version": mtime})
    return JSONResponse({"version": 0})



if(__name__) == '__main__':
        import uvicorn
        uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8080,
        reload  = True
    )

