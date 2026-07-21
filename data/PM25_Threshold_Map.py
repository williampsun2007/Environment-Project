'''
Loads 2020 baseline PM2.5 data, masks to China, and plots a red/blue
map flagging grid cells at or above 35 ug/m3 vs. below it.
'''

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from common import build_in_china_mask

fig = plt.figure(figsize = (15, 12))
ax = plt.axes(projection = ccrs.PlateCarree())

ds = xr.open_dataset("2020_Base_Data/PM25.nc")

in_china = build_in_china_mask(ds["lon"].values, ds["lat"].values)

data = ds["pred_PM25"].mean(dim = "time").values.copy()

colors_map = np.where(data >= 35, 1, 0)
colors_map = np.where(in_china, colors_map, np.nan)

provinces = cfeature.NaturalEarthFeature(
    category = 'cultural',
    name = 'admin_1_states_provinces_lines',
    scale = '50m',
    facecolor = 'none'
)

ax.pcolormesh(ds["lon"], ds["lat"], colors_map, cmap = 'coolwarm', vmin = 0, vmax = 1)
ax.coastlines()
ax.add_feature(cfeature.BORDERS)
ax.add_feature(provinces, edgecolor = 'black', linewidth = 0.5)

plt.title("China PM2.5 2020: Red = ≥35, Blue = <35")
plt.savefig("2020_Base_Data/Area over 35.png")
plt.show()
