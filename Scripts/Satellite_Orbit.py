import numpy as np
import matplotlib.pyplot as plot
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import HTML

# This is just a little animation to get a basic idea of what's going on. It's not completely physically accurate, but it is a good python exercise.

# This is a workaround for the lack of equal aspect ratio. Otherwise the sphere will come out lookin funny.
def set_axes_equal(ax):
    ranges = [ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()]
    centers = [(r[1] + r[0]) / 2 for r in ranges]
    max_range = max([abs(r[1] - r[0]) for r in ranges]) / 2
    for ctr, ax_set in zip(centers, [ax.set_xlim3d, ax.set_ylim3d, ax.set_zlim3d]):
        ax_set(ctr - max_range, ctr + max_range)

# Earthy parameters in km
a = 6378    # equatorial radius

# satellite orbital radius
s = 9000

# Tha oblate spheroid
u = np.linspace(0, np.pi, 100)
v = np.linspace(0, 2*np.pi, 100)
u, v = np.meshgrid(u, v)

x_earth = a * np.cos(u) * np.sin(v)
y_earth = a * np.sin(u) * np.sin(v)
z_earth = a * np.cos(v)

# Satellite position function
def satellite_position(theta):
    x = s * np.cos(theta)
    y = s * np.sin(theta)
    z = 0
    return x, y, z

fig = plot.figure(figsize = (7, 7))
ax = fig.add_subplot(111, projection = '3d')

max_range = s + 500
ax.set_xlim([-max_range, max_range])
ax.set_ylim([-max_range, max_range])
ax.set_zlim([-max_range, max_range])

ax.set_label('x (km)')
ax.set_ylabel('y (km)')
ax.set_zlabel('z (km)')
ax.set_title('Earth with satellite')

# Satellite starting point
satellite_x, satellite_y, satellite_z = satellite_position(0)
satellite, = ax.plot([satellite_x], [satellite_y], [satellite_z], 'go', markersize = 8)

Earth = [ax.plot_surface(x_earth, y_earth, z_earth, color = 'blue', alpha = 0.6, rstride = 2, cstride = 2, edgecolor = 'none')]

def update(frame):
    angle_rad = np.radians(frame)

    x_rotate = x_earth * np.cos(angle_rad) - y_earth * np.sin(angle_rad)
    y_rotate = x_earth * np.sin(angle_rad) + y_earth * np.cos(angle_rad)

    Earth[0].remove()
    Earth[0] = ax.plot_surface(x_rotate, y_rotate, z_earth, color = 'blue', alpha = 0.6, rstride = 2, cstride = 2, edgecolor = 'none')

    theta = np.radians(frame * 3)
    x_satellite, y_satellite, z_satellite = satellite_position(theta)
    satellite.set_data([x_satellite], [y_satellite])
    satellite.set_3d_properties([z_satellite])

    return Earth + [satellite]

set_axes_equal(ax)

# Animate boiiiieeeee
ani = FuncAnimation(fig, update, frames = np.arange(0, 360, 2), interval = 60, blit = False)

ani.save('Assets/Satellite_orbit.gif', writer = 'pillow', fps = 30)