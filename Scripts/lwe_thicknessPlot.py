import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.widgets import RadioButtons, Slider
from matplotlib.gridspec import GridSpec

#### This script makes use of the lwe_thickness variable read from the GRACE satellite mission. The topography is from the SRTM (Shuttle Radar Topography Mission) via using the python elevation package (pip install elevation, elevation --help, elevation --output srtm.tif --bounds -180 -90 180 90)

dataset = xr.open_dataset('C:/Users/spyro/OneDrive/Desktop/Python Projects/TopoGravCorrelator/Data/GRACE/GRCTellus.JPL.200204_202503.GLO.RL06.3M.MSCNv04CRI.nc')

# print(dataset)


# time indexing
lwe = dataset['lwe_thickness']

n_times = lwe.sizes['time']
print('Number of monthly timesteps:', n_times)


# Gravity anomaly from lwe-thickness using the Bouguer-slab approximation
G = 6.67e-11
rho = 1000.0    # water density
cm_to_m = 0.01

delta_h = lwe * cm_to_m # conversion from cm to m
delta_g = 2 * np.pi * G * rho * delta_h
delta_g_mGal = delta_g / 1e-5   # converting from m/s^2 to mGal

print(lwe)

# slider labels
time_labels = [str(t)[:10] for t in lwe['time'].values]

## time for a global state
current_choice = 'lwe'
current_time_index = 0

## Now for the figure itself. We usin gridspec for this one. What? It's an excuse to learn how to use it. This whole project is partly so I can learn python.
fig = plt.figure(figsize = (12, 6))

gs = GridSpec(nrows = 3, ncols = 4, height_ratios = [20, 0.5, 1.5], width_ratios = [5, 0.2, 0.15, 1.4], hspace = 0.02, wspace = 0.05)

# this is the axis set for the figure
ax_map = fig.add_subplot(gs[0, 0], projection = ccrs.PlateCarree())

ax_cbar = fig.add_subplot(gs[0:2, 2])

# This serves as a set of axes for the buttons on the left of the figure
ax_radio = fig.add_subplot(gs[2, 3], facecolor = 'lightgrey')

ax_slider = fig.add_subplot(gs[2, 0], facecolor = 'white')

time_slider = Slider(
    ax = ax_slider,
    label = 'time',
    valmin = 0,
    valmax = n_times - 1,
    valinit = current_time_index,
    valstep = 1,
    valfmt = '%d',
)

# Dem dere plottin function
def plot_data():
    global ax_map, ax_cbar, current_choice, current_time_index

    ax_map.clear()
    ax_cbar.clear()

    ax_map.set_global()
    ax_map.coastlines()
    ax_map.add_feature(cfeature.BORDERS, linewidth = 0.5)
    ax_map.gridlines(draw_labels = True)

    current_lwe = lwe.isel(time = current_time_index)
    delta_g_mgal = delta_g_mGal.isel(time = current_time_index)

    if current_choice == 'LWE':
        mesh = current_lwe.plot(
            ax = ax_map,
            transform = ccrs.PlateCarree(),
            cmap = 'RdBu',
            add_colorbar = False,
        )
        ax_map.set_title('Liquid Water Equivalent Thickness (cm)')

        cbar = fig.colorbar(
            mesh,
            cax = ax_cbar,
            orientation = 'vertical',
        )
        cbar.set_label('LWE (cm)')
    else:
        mesh = delta_g_mgal.plot(
            ax = ax_map,
            transform = ccrs.PlateCarree(),
            cmap = 'PuOr',
            add_colorbar = False,
        )
        ax_map.set_title('Gravity Anomaly from LWE (mGal)')

        cbar = fig.colorbar(
            mesh,
            cax = ax_cbar,
            orientation = 'vertical',
        )
        cbar.set_label('Δg (mGal)')
        
    fig.canvas.draw_idle()

def on_radio_clicked(label):
    global current_choice
    current_choice = 'LWE' if label == 'LWE' else 'Gravity'
    plot_data()

def on_slider_changed(val):
    global current_time_index
    current_time_index = int(val)
    plot_data()

radio = RadioButtons(ax_radio, ('LWE', 'Gravity from LWE'))
radio.on_clicked(on_radio_clicked)

time_slider.on_changed(on_slider_changed)

plot_data()

plt.show()


