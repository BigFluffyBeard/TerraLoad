from skyfield.api import load, EarthSatellite
import numpy as np
import matplotlib.pyplot as plot
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import glob
from datetime import timedelta

# Skyfield wants a timescale. Needs leap seconds to turn the lte epoch date to a .epoch Time object.
ts = load.timescale()

# Can grab all the TLE files just by grabbing the entire folder of txt files
tle_files = glob.glob('Location of the folder containing TLE .txt files')
satellites = []

# Preparin a figure ahead of time
fig = plot.figure(figsize = (12, 6))
ax = plot.axes(projection = ccrs.PlateCarree())
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth = 0.5)
gridlines = ax.gridlines(draw_labels = True)
gridlines.order = 0
colors= ['purple', 'darkgreen']


for tle_path in tle_files:
    with open(tle_path, 'r', encoding = 'utf-8') as f:
        lines = f.read().splitlines()
        if len(lines) >= 3:
            name = lines[0].strip()
            line1 = lines[1].strip()
            line2 = lines[2].strip()
            satellite = EarthSatellite(line1, line2, name, ts)
            satellites.append(satellite)

print(f'Loaded {len(satellites)} satellites.')

# Time array. Start at the present time (0) and count up to 95 minutes from "now" (which is counted as 94 instead of 95, because we start at 0). You're at "now" now, but you missed it! Just now! Everything that happened then is happening now!
# minutes = np.arange(0, 95, 1)  # 0 (current) minutes to 94 minutes
present_time = ts.now()
# times = ts.utc(present_time.utc_datetime() + np.array([np.timedelta64(m, 'm') for m in minutes]))
times = ts.utc([present_time.utc_datetime() + timedelta(minutes=i) for i in range(95)])    # Skyfield's built-in time-step function

for i, sat in enumerate(satellites):
    geocentric_positions = sat.at(times)
    positions_km = geocentric_positions.position.km # takes the shape (3, N)
    print(f"{sat.name}: {positions_km.shape[1]} ! Oi! U er' that? U got yer stinkin computations! ")

    # Plottin!
    subpoints = geocentric_positions.subpoint()
    latitudes = subpoints.latitude.degrees
    longitudes = subpoints.longitude.degrees

    ### For this next little part here, I want little arrow tickmarks on the satellite tracks to show their direction of travel.
    # position change from point to point
    delta_longitudes = np.diff(longitudes)
    delta_latitudes = np.diff(latitudes)

    # arrow positions (using midpoint formula)
    midpoint_longitudes = (longitudes[:-1] + longitudes[1:]) / 2
    midpoint_latitudes = (latitudes[:-1] + latitudes[1:]) / 2

    # To acquire consistant arrow size, we'll need some normalization
    The_norm = np.sqrt(delta_longitudes**2 + delta_latitudes**2)
    u = delta_longitudes / The_norm
    v = delta_latitudes / The_norm

    # The plot. Nothing wrong is happenin here
    ax.plot(longitudes, latitudes, transform = ccrs.Geodetic(), color = colors[i], linewidth = 1.5, label = sat.name)

    # Now we need a quiver
    # Just plot them every...I don't know...nth point
    step = 10
    ax.quiver(midpoint_longitudes[::step], midpoint_latitudes[::step], u[::step], v[::step], transform = ccrs.PlateCarree(), color = 'red', scale = 20, width = 0.003, headwidth = 3, headlength = 4)

plot.title('Simulated Groundtracks of GRACE-FO 1 and ICEsat-2 satellites over 95 minutes')
plot.legend()
plot.show()

# fig.savefig('Assets/Satellite Groundtracks.png', format = 'png')