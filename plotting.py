import sqlite3
import os
import math
import matplotlib.pyplot as plt
import re

db_path = os.path.join(os.path.dirname(__file__), 'hotspots.db')
available_channels = ['A', 'B', 'C', 'D', 'E']

def calculate_distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def is_interfering(x1, y1, channel1, x2, y2, channel2):
    return calculate_distance(x1, y1, x2, y2) <= 275 and channel1 == channel2

def get_latest_column():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("PRAGMA table_info(hotspots)")
        columns = cursor.fetchall()
        iteration_columns = [col[1] for col in columns if re.match(r'iteration_\d+', col[1])]
        if not iteration_columns:
            return "channel"
        return max(iteration_columns, key=lambda x: int(re.search(r'_(\d+)', x).group(1)))

def load_hotspots():
    latest_column = get_latest_column()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f"""
            SELECT id, x, y, COALESCE({latest_column}, channel) as channel FROM hotspots
        """)
        return [{'id': row[0], 'x': row[1], 'y': row[2], 'channel': row[3]} for row in cursor.fetchall()]

def count_interfering_hotspots(hotspots):
    count = 0
    for i in range(len(hotspots)):
        x1, y1, ch1 = hotspots[i]['x'], hotspots[i]['y'], hotspots[i]['channel']
        for j in range(i + 1, len(hotspots)):
            x2, y2, ch2 = hotspots[j]['x'], hotspots[j]['y'], hotspots[j]['channel']
            if is_interfering(x1, y1, ch1, x2, y2, ch2):
                count += 1
    return count

def optimise_channels(hotspots, available_channels):
    updatedch = {}
    updated_hotspots = [dict(h) for h in hotspots]

    def count_interference_for(hlist):
        return count_interfering_hotspots(hlist)

    original_interference = count_interference_for(updated_hotspots)

    for i in range(len(updated_hotspots)):
        h1 = updated_hotspots[i]
        for j in range(i + 1, len(updated_hotspots)):
            h2 = updated_hotspots[j]
            if is_interfering(h1['x'], h1['y'], h1['channel'], h2['x'], h2['y'], h2['channel']):
                current_channel = h2['channel']
                best_channel = current_channel
                lowest_interference = original_interference

                for ch in available_channels:
                    if ch == current_channel:
                        continue
                    temp_hotspots = [dict(h) for h in updated_hotspots]
                    temp_hotspots[j]['channel'] = ch
                    new_interference = count_interference_for(temp_hotspots)
                    if new_interference < lowest_interference:
                        best_channel = ch
                        lowest_interference = new_interference

                if best_channel != current_channel:
                    updated_hotspots[j]['channel'] = best_channel
                    updatedch[h2['id']] = best_channel
                    original_interference = lowest_interference

    return updatedch, updated_hotspots

def iterate_channels(all_hotspots):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(hotspots)")
        columns = cursor.fetchall()
        iteration_columns = [col[1] for col in columns if re.match(r'iteration_\d+', col[1])]
        next_number = max([int(re.search(r'_(\d+)', col).group(1)) for col in iteration_columns], default=0) + 1
        new_column_name = f'iteration_{next_number}'
        cursor.execute(f"ALTER TABLE hotspots ADD COLUMN {new_column_name} TEXT")
        for h in all_hotspots:
            cursor.execute(
                f"UPDATE hotspots SET {new_column_name} = ? WHERE id = ?",
                (h['channel'], h['id'])
            )

        conn.commit()
        print(f"Stored full channel state in column '{new_column_name}'")


def plothotspots():
    latest_column = get_latest_column()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, x, y, COALESCE({latest_column}, channel) as channel FROM hotspots")
        hotspotsplot = cursor.fetchall()

    interfering_hotspots = set()
    for i in range(len(hotspotsplot)):
        x1, y1, ch1 = hotspotsplot[i][1], hotspotsplot[i][2], hotspotsplot[i][3]
        for j in range(i + 1, len(hotspotsplot)):
            x2, y2, ch2 = hotspotsplot[j][1], hotspotsplot[j][2], hotspotsplot[j][3]
            if is_interfering(x1, y1, ch1, x2, y2, ch2):
                interfering_hotspots.add(i)
                interfering_hotspots.add(j)

    x_coords = [h[1] for h in hotspotsplot]
    y_coords = [h[2] for h in hotspotsplot]
    channels = [h[3] for h in hotspotsplot]

    channel_colors = {'A': 'gray', 'B': 'cyan', 'C': 'green', 'D': 'purple', 'E': 'orange'}
    face_colors = [channel_colors.get(ch, 'gray') for ch in channels]
    edge_colors = ['red' if idx in interfering_hotspots else 'black' for idx in range(len(hotspotsplot))]

    plt.figure(figsize=(10, 8))
    plt.scatter(x_coords, y_coords, c=face_colors, edgecolors=edge_colors, s=50, linewidths=1)

    for i in range(len(hotspotsplot)):
        x1, y1, ch1 = hotspotsplot[i][1], hotspotsplot[i][2], hotspotsplot[i][3]
        for j in range(i + 1, len(hotspotsplot)):
            x2, y2, ch2 = hotspotsplot[j][1], hotspotsplot[j][2], hotspotsplot[j][3]
            if is_interfering(x1, y1, ch1, x2, y2, ch2):
                plt.plot([x1, x2], [y1, y2], 'r-', linewidth=1, alpha=0.6)

    plt.title(f"Hotspot Locations (Latest: {latest_column}) with Interference Highlighted")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{latest_column}.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    hotspots = load_hotspots()
    prev_interference = count_interfering_hotspots(hotspots)
    print(f"Previous Interference Count: {prev_interference}")

    updatedch, new_hotspots = optimise_channels(hotspots, available_channels)

    if not updatedch:
        print("No updates made. Network already optimised or no further improvements possible.")
    else:
        iterate_channels(new_hotspots)
        hotspots = load_hotspots()
        new_interference = count_interfering_hotspots(hotspots)
        print(f"New Interference Count: {new_interference}")

    plothotspots()

