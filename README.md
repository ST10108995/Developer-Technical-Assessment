# Developer-Technical-Assessment

## BRIEFING:
There are 1,000 Wi-Fi hotspots in a 5x5km area. Each hotspot is at a random location in this area and is never closer than 50m from it's neighbour. Each hotspot broadcasts on one of 5 different channels which are initially assigned randomly. If a hotspot is within 275m of another hotspot and is on the same channel they will interfere.

1. Write a program that will generate the Wi-Fi hotspots as described above. The data should be stored in an appropriate data structure such as a list, dictionary, dataframe or sqlite database.

2. Extend the program by getting it to minimise the number of hotspots that are interfering with each other by changing the channel on which they are broadcasting. This will most likely be an iterative process and you need to produce a plot that shows how the number of interfering hotspots changes with each iteration.

3. Finally, produce a plot showing the hotspot locations. The colour of the dot should indicate the channel that the hotspot is on. Hotspots that are being interfered with must have a red border, otherwise they must have a black border. If two hotspots are interfering with each other they should be joined by a red line.
