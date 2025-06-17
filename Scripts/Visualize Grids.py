import rasterio
import matplotlib.pyplot as plt
from rasterio.warp import reproject, Resampling
from rasterio.transform import Affine
import numpy as np
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
import xarray as xr

### This script is primarily for just visualizing what the affine transforms are doing. It's important to know what your code does.

GRACE = xr.open_dataset('Path to Grace dataset')
latitude = GRACE.lat.values
longitude = GRACE.lon.values

nlatitude = len(latitude)
nlongitude = len(longitude)
latitude_res = abs(latitude[1] - latitude[0])
longitude_res = abs(longitude[1] - longitude[0])
latitude_min = float(latitude.min())
latitude_max = float(latitude.max())
longitude_min = float(longitude.min())
longitude_max = float(longitude.max())

GRACE_transform = Affine(longitude_res, 0, longitude_min, 0, -latitude_res, latitude_max)

downsampled_topography = np.empty((nlatitude, nlongitude), dtype = np.float32)
ETOPO_path = ("Path to ETOPO dataset")

with rasterio.open(ETOPO_path) as src:
    reproject(
        source = rasterio.band(src, 1),
        destination = downsampled_topography,
        src_transform = src.transform,
        src_crs = src.crs,
        dst_transform = GRACE_transform,
        dst_crs = "EPSG:4326",
        resampling = Resampling.bilinear
    )

Longitude, Latitude = np.meshgrid(longitude, latitude)

fig, ax = plt.subplots(figsize = (14, 7), subplot_kw = {'projection': ccrs.PlateCarree()})
ax.set_title("ETOPO (downsampled) with GRACE Affine Grid Overlay")

ax.coastlines()
ax.add_feature(cfeature.BORDERS, linewidth = 0.5)
ax.add_feature(cfeature.LAND, facecolor = 'lightgray')
ax.add_feature(cfeature.OCEAN, facecolor = 'lightblue')

im = ax.pcolormesh(Longitude, Latitude, downsampled_topography, cmap = 'terrain', shading = 'auto', transform = ccrs.PlateCarree())

for i in range(0, nlongitude, 12):
    ax.plot([longitude[i]] * nlatitude, latitude, color = 'black', linewidth = 0.5, transform = ccrs.PlateCarree(), alpha = 0.3)
    
for j in range(0, nlatitude, 12):
    ax.plot(longitude, [latitude[j]] * nlongitude, color = 'black', linewidth = 0.5, transform = ccrs.PlateCarree(), alpha = 0.3)

cbar = plt.colorbar(im, orientation = 'vertical', label = 'Geoid Height (m)', ax = ax, shrink = 0.7, pad = 0.05)

plt.tight_layout()
plt.show()
