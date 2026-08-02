'''
Map of PM2.5 concentration change from the EPNZCA scenario with further 10% reduction in PM2.5 in Hebei
'''

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs
import xarray as xr
import cartopy.feature as cfeature
from common import build_in_china_mask

ds = xr.open_dataset("2020_Base_Data/PM25.nc")

in_china = build_in_china_mask(ds["lon"].values, ds["lat"].values)

provinces = cfeature.NaturalEarthFeature(
    category = 'cultural',
    name = 'admin_1_states_provinces_lines',
    scale = '50m',
    facecolor = 'none'
)

file_base = Path("NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_early-peak-net-zero-clean-air_2020Met.nc")
file = Path("NC Files and Emission Reports - OP1 Scenarios/EmissionReductions_EPNZCA2035_OP1_PR3_SP5_10pctRed_2020Met_results.nc")

pollutant = "PM2.5"
    
scenario = f"EPNZCA Scenario with Further 10% Reduction in PM2.5 in Hebei"
        
base = xr.open_dataset(file_base)["pred_PM25"].mean(dim = "time").values
pm25 = xr.open_dataset(file)["pred_PM25"].mean(dim = "time").values

delta = base - pm25
delta = np.where(in_china, delta, np.nan)
    
fig = plt.figure(figsize = (18, 10))
ax = fig.add_axes([0.05, 0.05, 0.75, 0.9], projection = ccrs.PlateCarree())
    
cmap = plt.get_cmap("RdBu").copy()
cmap.set_bad(alpha = 0)
vmax = np.nanmax(np.abs(delta))
norm = TwoSlopeNorm(vmin = -vmax, vcenter = 0, vmax = vmax)

im = ax.pcolormesh(ds["lon"].values, ds["lat"].values, delta, cmap = cmap, norm = norm)
    
cax = fig.add_axes([0.82, 0.1, 0.02, 0.8])

cbar = plt.colorbar(im, cax = cax)
cbar.set_label("ΔPM2.5 (baseline − perturbed), µg/m³")
    
ax.coastlines()
ax.add_feature(cfeature.BORDERS)
ax.add_feature(provinces, edgecolor = 'black', linewidth = 0.5)
    
ax.set_title(
    f"EPNZCA Scenario with Further 10% Reduction in PM2.5 in Hebei\n"
    f"ΔPM2.5 (baseline − perturbed) from extra 10% PM2.5 cut in Hebei\n",
    fontsize = 10
)
    
plt.tight_layout(rect = [0, 0, 0.85, 0.95])
plt.savefig(f"Emission Files/OP1 Scenario Analysis/Population_PM_Concentration_Map_Hebei_PM25.png")
plt.close()
    
print("Finished!")
    
    
    
    
    
