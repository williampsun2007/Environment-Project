'''
Loads PM2.5 model output for two scenarios (on-time-peak vs.
early-peak-net-zero, 2024 met year), masks to China, and plots the
spatial difference in mean PM2.5 concentration between them as a map.
'''

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from common import build_in_china_mask

fig = plt.figure(figsize = (15, 12))
ax = plt.axes(projection = ccrs.PlateCarree())

ds_ontime = xr.open_dataset("NC Files and Emission Reports/EmissionReductions2035_on-time-peak-clean-air_2024Met.nc")
ds_earlypeak = xr.open_dataset("NC Files and Emission Reports/EmissionReductions2035_early-peak-net-zero-clean-air_2024Met.nc")

in_china = build_in_china_mask(ds_ontime["lon"].values, ds_ontime["lat"].values)
        
difference = ds_ontime["pred_PM25"].mean(dim = "time").values.copy() - ds_earlypeak["pred_PM25"].mean(dim = "time").values.copy()
difference[~in_china] = np.nan

min_value = np.nanmin(difference)
max_value = np.nanmax(difference)

im = ax.pcolormesh(ds_ontime["lon"], ds_ontime["lat"], difference, vmin = min(min_value, -max_value), vmax = max(-min_value, max_value))

ax.coastlines()
ax.add_feature(cfeature.BORDERS)

plt.title("Difference in PM2.5 Concentration from OPTCA to EPNZCA Scenarios throughout China, 2024 Met Year")
plt.colorbar(im, label = "PM2.5 Concentration Decrease from OTPCA to EPNZCA")
plt.savefig("Emission Files/PM2.5_Difference_OTPCA_to_EPNZCA_2024Met.png")
plt.show()

