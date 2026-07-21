'''
For each pollutant/reduction-percent scenario, averages PM2.5 output
across multiple download batches, then maps 2020 population colored
gray (<25 ug/m3) or red (>=25 ug/m3) by exposure, saving one PNG map
per scenario.
'''

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs
import xarray as xr
import cartopy.feature as cfeature
from common import build_in_china_mask

pop_grid_2020 = np.load("Emission Files/pop_grid_wrf_2020.npy")

ds = xr.open_dataset("2020_Base_Data/PM25.nc")

in_china = build_in_china_mask(ds["lon"].values, ds["lat"].values)

pop_grid_2020[pop_grid_2020 == 0] = 1
pop_grid_2020[~in_china] = np.nan

provinces = cfeature.NaturalEarthFeature(
    category = 'cultural',
    name = 'admin_1_states_provinces_lines',
    scale = '50m',
    facecolor = 'none'
)

nc_files = list(Path("Scenario Percentage Decrease Downloads/Batch1, 7-2-2026").glob("*.nc"))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch2, 7-3-2026").glob("*.nc")))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch3, 7-4-2026").glob("*.nc")))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch4, 7-5-2026").glob("*.nc")))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch5, 7-6-2026").glob("*.nc")))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch6, 7-7-2026").glob("*.nc")))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch7, 7-8-2026").glob("*.nc")))
nc_files.extend(list(Path("Scenario Percentage Decrease Downloads/Batch8, 7-9-2026").glob("*.nc")))
nc_files = sorted(nc_files)

dictionary = {}
for file in nc_files:
    parts = file.stem.split("_")
    pollutant = parts[1]
    pct_reduction = parts[2].split("pct")[0]
    
    scenario = f"{pollutant}_{pct_reduction}"
    if dictionary.get(scenario) is None:
        dictionary[scenario] = []
        
    pm25 = xr.open_dataset(file)["pred_PM25"].mean(dim = "time").values
    
    dictionary[scenario].append(pm25)

for scenario, values in dictionary.items():
    pm25 = np.mean(values, axis = 0)
    
    fig = plt.figure(figsize = (18, 10))
    ax = fig.add_axes([0.05, 0.05, 0.75, 0.9], projection = ccrs.PlateCarree())
    
    cmap_gray = LinearSegmentedColormap.from_list('custom_grays', ['#f0f0f0', '#1a1a1a'])
    cmap_gray.set_bad(alpha = 0)
    norm_gray = PowerNorm(gamma = 0.5, vmin = 1, vmax = 5_000_000)

    cmap_red = LinearSegmentedColormap.from_list('custom_reds', ['#ffcccc', '#8b0000'])
    cmap_red.set_bad(alpha = 0)
    norm_red = PowerNorm(gamma = 0.5, vmin = 1, vmax = 5_000_000)

    below_25_pop = np.where((pm25 < 25) & in_china, pop_grid_2020, np.nan)
    above_25_pop = np.where((pm25 >= 25) & in_china, pop_grid_2020, np.nan)

    im_gray = ax.pcolormesh(ds["lon"].values, ds["lat"].values, below_25_pop, cmap = cmap_gray, norm = norm_gray)
    im_red = ax.pcolormesh(ds["lon"].values, ds["lat"].values, above_25_pop, cmap = cmap_red, norm = norm_red)
    
    cax_gray = fig.add_axes([0.82, 0.52, 0.02, 0.35])
    cax_red = fig.add_axes([0.82, 0.1, 0.02, 0.35])

    cbar_gray = plt.colorbar(im_gray, cax = cax_gray)
    cbar_gray.set_label('Population < 25 µg/m³', fontsize = 9)

    cbar_red = plt.colorbar(im_red, cax = cax_red)
    cbar_red.set_label('Population ≥ 25 µg/m³', fontsize = 9)
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(provinces, edgecolor = 'black', linewidth = 0.5)
    
    parts = scenario.split("_")
    pollutant = parts[0]
    pct_reduction = parts[1]
    
    ax.set_title(
        f"China Population Distribution by PM2.5 Exposure (2020 Pop.)\n"
        f"Gray: < 25 µg/m³ | Red: ≥ 25 µg/m³ | Color Intensity = Population Density\n"
        f"Pollutant: {pollutant} | Percent Reduction: {pct_reduction}%",
        fontsize = 10
    )
    
    plt.tight_layout(rect = [0, 0, 0.85, 0.95])
    plt.savefig(f"Emission Files/Percentage Reduction Sensitivity Figures/Maps/{pollutant}_{pct_reduction}_map.png")
    plt.close()
    
print("Finished!")
    
    
    
    
    
