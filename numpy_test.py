import numpy as np
from datetime import datetime, timezone

if __name__ == "__main__":
    iso_utc_now = datetime.now(timezone.utc).isoformat()
    event_time = iso_utc_now

    # Create an empty 2D array with shape (0, 3)
    np_data = np.empty((0, 3))

    print("Shape of np_data:", np_data.shape)

    # Append a new row to the array
    new_row = np.array([[event_time, 0, 3]])
    np_data = np.vstack((np_data, new_row))

    print("Shape of np_data:", np_data.shape)

    # Append another new row to the array
    another_row = np.array([[4, 5, 6]])
    np_data = np.vstack((np_data, another_row))

    print("Shape of np_data:", np_data.shape)

    another_row = np.array([[4, 5, 6]])
    np_data = np.vstack((np_data, another_row))

    print("Shape of np_data:", np_data.shape)

    np_data = np.append(np_data, [[7, 8, 9]], axis=0)


    print(np_data)
    print("Shape of np_data:", np_data.shape)
