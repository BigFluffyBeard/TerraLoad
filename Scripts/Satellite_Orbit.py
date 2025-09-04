import numpy as np
import matplotlib.pyplot as plot
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from skyfield.api import load, EarthSatellite
from IPython.display import HTML
import matplotlib.image as mapimg
from datetime import timedelta

# This is just a little animation to get a basic idea of what's going on. It's not completely physically accurate, but it is a good python exercise.

# Loadin TLEs
timescale = load.timescale()
def load_satellite(tle_files):
    with open(tle_files, 'r', encoding = 'utf-8') as f:
        lines = f.read().splitlines()
        return EarthSatellite(lines[1], lines[2],  lines[0], timescale)

# Gettin Satellite information.
grace = load_satellite('location of your GRACE TLE .txt file')
icesat = load_satellite('location of your ICESat-2 TLE .txt file')

# let's go for 90 minute orbit simulations
minutes = np.arange(0, 95, 1)
times = timescale.utc(2025, 7, 3, 0, minutes)

# Position arrays for each satellite
def get_xyz(satellite, times):
    geocentric = satellite.at(times)
    return geocentric.position.km

xg, yg, zg = get_xyz(grace, times)
xI, yI, zI = get_xyz(icesat, times)

# Earthy parameters in km
a = 6378    # equatorial radius

# Tha oblate spheroid
u = np.linspace(0, np.pi, 100) # Matching image with longitude
v = np.linspace(0, 2*np.pi, 100)   # Matching image with latitude
u, v = np.meshgrid(u, v)

x_earth = a * np.cos(u) * np.sin(v)
y_earth = a * np.sin(u) * np.sin(v)
z_earth = a * np.cos(v)



# Initial plot
fig = plot.figure(figsize = (8, 8))
ax = fig.add_subplot(111, projection = '3d')
ax.set_xlim([-10000, 10000])
ax.set_ylim([-10000, 10000])
ax.set_zlim([-10000, 10000])
ax.set_title('GRACE-FO and ICESat-2 in orbit')

# Plottin Earth and Satellites on said above plot.
Earth = [ax.plot_surface(x_earth, y_earth, z_earth, color = 'blue', alpha = 0.5, edgecolor = 'none')]
Grace_dot, = ax.plot([xg[0]], [yg[0]], [zg[0]], 'go', label = 'GRACE-FO', markersize = 6)
Icesat_dot, = ax.plot([xI[0]], [yI[0]], [zI[0]], 'ro', label = 'ICESat-2', markersize = 6)

ax.legend(loc = 'upper right')  # setting a fixed location for the legend. Gives matplotlib less to do

# This is a workaround for the lack of equal aspect ratio. Otherwise the sphere will come out lookin funny.
def set_axes_equal(ax):
    ranges = [ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()]
    centers = [(r[1] + r[0]) / 2 for r in ranges]
    max_range = max([abs(r[1] - r[0]) for r in ranges]) / 2
    for ctr, ax_set in zip(centers, [ax.set_xlim3d, ax.set_ylim3d, ax.set_zlim3d]):
        ax_set(ctr - max_range, ctr + max_range)

def update(frame):
    Grace_dot.set_data([xg[frame]], [yg[frame]])
    Grace_dot.set_3d_properties([zg[frame]])

    Icesat_dot.set_data([xI[frame]], [yI[frame]])
    Icesat_dot.set_3d_properties([zI[frame]])
    
    # Rotatin Earth!
    angle_rad = np.radians(frame)
    x_rot = x_earth * np.cos(angle_rad) - y_earth * np.sin(angle_rad)
    y_rot = x_earth * np.sin(angle_rad) + y_earth * np.cos(angle_rad)
    Earth[0].remove()
    Earth[0] = ax.plot_surface(x_rot, y_rot, z_earth, color='blue', alpha=0.5, edgecolor='none')

    return Earth + [Grace_dot, Icesat_dot]

# Animate boiiiieeeee
ani = FuncAnimation(fig, update, frames = range(len(times)), interval = 100)
# ani.save('Assets/Orbital_dual.gif', writer = 'pillow', fps = 15)