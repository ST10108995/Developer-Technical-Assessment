import random
import sqlite3
import os
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

DB_PATH = os.path.join(os.path.dirname(__file__), 'hotspots.db')

def too_close(x, y, coords, min_distance=50):
    if not coords:
        return False
    tree = KDTree(coords)
    return len(tree.query_ball_point([x, y], min_distance)) > 0

def create_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotspots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                channel TEXT NOT NULL
            )
        ''')
        conn.commit()

def channelgen():
    return chr(random.randint(65, 69))

def rng():
    return random.randint(1, 5000)

def generate_hotspots(target_count, min_distance=50):
    hotspots = []
    coords = []
    
    while len(hotspots) < target_count:
        x, y = rng(), rng()
        ch = channelgen()

        if not too_close(x, y, coords, min_distance):
            hotspots.append((x, y, ch))
            coords.append((x, y))
    
    return hotspots
    
def write_hotspots_to_db(hotspots):
    create_table()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO hotspots (x, y, channel) VALUES (?, ?, ?)
        ''', hotspots)
        conn.commit()
        print(f"{len(hotspots)} hotspots written to database.")

def plothotspots():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT x, y, channel FROM hotspots")
        hotspots = cursor.fetchall()

    x_coords = [h[0] for h in hotspots]
    y_coords = [h[1] for h in hotspots]
    channels = [h[2] for h in hotspots]

    channel_colors = {'A': 'gray', 'B': 'cyan', 'C': 'green', 'D': 'purple', 'E': 'orange'}
    face_colors = [channel_colors.get(ch, 'gray') for ch in channels]

    plt.figure(figsize=(10, 8))
    plt.scatter(x_coords, y_coords, c=face_colors, edgecolors='black', s=50, linewidths=1)
    plt.title("Hotspot Locations")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("plot.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    try:
        hotspots = generate_hotspots(1000)
        write_hotspots_to_db(hotspots)
    except (RuntimeError, ValueError) as e:
        print(e)

    plothotspots()
