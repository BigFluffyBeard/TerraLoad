import xarray as xr
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.warp import reproject, Resampling
from rasterio.transform import Affine
import cartopy.crs as ccrs
import cartopy.feature as cfeature

### This is the script that works with the ETOPO 2022 topography data, specifically the geoid height dataset. If I'm not wrong, a static geoid height map wcan act as an equilibrium gravitational potential, which makes sense with the gravity simulations I can do with the GRACE dataset.

# Okay...so this is a massive array to plot here. Good thing I have a powerful system, this might have fried my laptop. Gotta drop down the memory usage here. Tis using up nearly 4 gigs of RAM for just plotting this array.

GRACE = xr.open_dataset('C:/Users/spyro/OneDrive/Desktop/Python Projects/TopoGravCorrelator/Data/GRACE/GRCTellus.JPL.200204_202503.GLO.RL06.3M.MSCNv04CRI.nc')

# GRACE spatial info
lat = GRACE.lat.values
lon = GRACE.lon.values
nlatitude = len(lat)
nlongitude = len(lon)
latitude_res = abs(lat[1] - lat[0])
longitude_res = abs(lon[1] - lon[0])
latitude_min = float(lat.min())
latitude_max = float(lat.max())
longitude_min = float(lon.min())
longitude_max = float(lon.max())

## Now we need an affine transform for the GRACE grid!
GRACE_transform = Affine(
    longitude_res, 0, longitude_min, 0, -latitude_res, latitude_max
)

# the output array that will hold the downsized topography
Topography_downsampled = np.empty((nlatitude, nlongitude), dtype = np.float32)

with rasterio.open("C:/Users/spyro/OneDrive/Desktop/Python Projects/TopoGravCorrelator/Data/ETOPO 2022 Geoid Height/ETOPO_2022_v1_30s_N90W180_geoid.tif") as src:
    reproject(
        source = rasterio.band(src, 1),
        destination = Topography_downsampled,
        src_transform = src.transform,
        src_crs = src.crs,
        dst_transform = GRACE_transform,
        dst_crs = "EPSG:4326",
        dst_resolution = (longitude_res, latitude_res),
        resampling = Resampling.bilinear
    )

# Now just gotta plot this
plt.figure(figsize = (12, 6))
ax = plt.axes(projection = ccrs.PlateCarree())
ax.set_global()
ax.coastlines(resolution = '110m')
ax.add_feature(cfeature.BORDERS, linewidth = 0.5)
ax.add_feature(cfeature.LAND, facecolor = 'lightgray')
ax.add_feature(cfeature.OCEAN, facecolor = 'lightblue')
ax.gridlines(draw_labels = True)

mesh = ax.pcolor(lon, lat, Topography_downsampled, cmap = 'cubehelix', shading = 'auto', transform = ccrs.PlateCarree())

plt.title("ETOPO 2022 Downsampled to GRACE Resolution")
cbar = plt.colorbar(mesh, ax = ax, orientation = 'vertical', pad = 0.02, shrink = 0.8)
cbar.set_label("Geoid Height (m)")
plt.tight_layout()

plt.savefig("Assets/ETOPO_downsample.png")
plt.show()