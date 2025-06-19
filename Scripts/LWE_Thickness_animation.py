import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

# GRACE dataset
dataset = xr.open_dataset('C:/Users/spyro/OneDrive/Desktop/Python Projects/TopoGravCorrelator/Data/GRACE/GRCTellus.JPL.200204_202503.GLO.RL06.3M.MSCNv04CRI.nc')
lwe = dataset['lwe_thickness']

# Constants
G = 6.67e-11
rho = 1000.0    # water density
cm_to_m = 0.01

delta_h = lwe * cm_to_m # conversion from cm to m
delta_g = 2 * np.pi * G * rho * delta_h
delta_g_mGal = delta_g / 1e-5   # converting from m/s^2 to mGal

# Which dataset do you want to animate?
mode = 'LWE'

# Plot set up
fig = plt.figure(figsize = (10, 5))
ax = plt.axes(projection = ccrs.PlateCarree())
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth = 0.5)
ax.gridlines(draw_labels = True)

# Initial plot at time 0
frame0 = lwe.isel(time = 0) if mode == 'LWE' else delta_g_mGal.isel(time = 0)
mesh = frame0.plot(ax = ax, transform = ccrs.PlateCarree(), cmap = 'RdBu' if mode == 'LWE' else 'PuOr', add_colorbar = True)
title = ax.set_title('')

def update(frame):
    data = lwe.isel(time = frame) if mode == 'LWE' else delta_g_mGal.isel(time = frame)
    mesh.set_array(data.values.flatten())
    title.set_text(f"{mode} - {str(lwe['time'].values[frame])[:10]}")
    return mesh,

ani = FuncAnimation(fig, update, frames = len(lwe['time']), interval =  200)

ani.save('grace_lwe_animation.gif', fps = 5)