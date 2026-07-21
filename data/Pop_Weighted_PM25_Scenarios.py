'''
For 2030 and 2035, computes the 2020-population-weighted mean PM2.5
for each of the 5 scenarios under both 2017 and 2020 baselines, then
plots grouped bar charts comparing them and saves each figure.
'''

from pathlib import Path
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import xarray as xr
from common import build_in_china_mask

ds = nc.Dataset("2017_Base_Data/PM25.nc")

in_china = build_in_china_mask(ds["lon"][:], ds["lat"][:])

pop_grid_2020 = np.load("Emission Files/pop_grid_wrf_2020.npy")
pop_china_2020 = pop_grid_2020.copy()
pop_china_2020 = np.nan_to_num(pop_china_2020, nan = 0.0)
pop_china_2020[~in_china] = 0
total_pop = pop_china_2020.sum()

scenarios = ["Baseline", "CleanAir", "OTPCA", "OTPNZCA", "EPNZCA"]
width = 0.35

fig, ax = plt.subplots(figsize = (10, 6))
for base_year in [2017, 2020]:
    nc_files_2030 = Path(f"NC Files and Emission Reports - {base_year} to 2030").glob("*.nc")
    dict_2030 = {}
    for file in nc_files_2030:
        if base_year == 2017:
            parts = file.stem.split("-2017-")
            scenario = parts[0]
        else:  
            parts = file.stem.split("_")
            scenario = parts[0].split("-2030-")[1]
    
        if dict_2030.get(scenario) is None:
            dict_2030[scenario] = []
        
        ds = xr.open_dataset(file)
        data = ds["pred_PM25"].mean(dim = "time").values
        data[~in_china] = 0
    
        mean_pm = (data * pop_china_2020).sum() / total_pop
        dict_2030[scenario].append(mean_pm)
    
    dict_2030_averages = [0] * 5
    for key, value in dict_2030.items():
        if key == "baseline":
            idx = 0
        elif key == "clean-air":
            idx = 1
        elif key == "on-time-peak-clean-air":
            idx = 2
        elif key == "on-time-peak-net-zero-clean-air":
            idx = 3
        elif key == "early-peak-net-zero-clean-air":
            idx = 4
        
        dict_2030_averages[idx] = sum(value) / len(value)
    
    if base_year == 2017:
        ax.bar(np.arange(1, 6) - width / 2, dict_2030_averages, width, label = "2017 Base", color = "skyblue")
    else:
        ax.bar(np.arange(1, 6) + width / 2, dict_2030_averages, width, label = "2020 Base", color = "orange")
    
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xticklabels(scenarios)
ax.set_xlabel("Scenario")
ax.set_ylabel("Population Weighted PM2.5 Concentration Mean")
ax.set_title("Population Weighted PM2.5 Concentration Mean Across Scenarios (2030)")
    
plt.legend()
plt.tight_layout()
plt.savefig("Emission Files/2020 to 2030, 2035 Population Weighted PM2.5 Mean/2030 (2020 Pop).png")
plt.show()

fig, ax = plt.subplots(figsize = (10, 6))
for base_year in [2017, 2020]:
    nc_files_2035 = Path(f"NC Files and Emission Reports - {base_year} to 2035").glob("*.nc")
    dict_2035 = {}
    for file in nc_files_2035:
        if base_year == 2017:
            scenario = file.stem.split("-2035-")[1].split("-2017-")[0]
        else:
            scenario = file.stem.split("_")[1]
    
        if dict_2035.get(scenario) is None:
            dict_2035[scenario] = []
        
        ds = xr.open_dataset(file)
        data = ds["pred_PM25"].mean(dim = "time").values
        data[~in_china] = 0
    
        mean_pm = (data * pop_china_2020).sum() / total_pop
        dict_2035[scenario].append(mean_pm)
    
    dict_2035_averages = [0] * 5
    for key, value in dict_2035.items():
        if key == "baseline":
            idx = 0
        elif key == "clean-air":
            idx = 1
        elif key == "on-time-peak-clean-air":
            idx = 2
        elif key == "on-time-peak-net-zero-clean-air":
            idx = 3
        elif key == "early-peak-net-zero-clean-air":
            idx = 4
        
        dict_2035_averages[idx] = sum(value) / len(value)
    
    if base_year == 2017:
        print(dict_2035_averages)
        ax.bar(np.arange(1, 6) - width / 2, dict_2035_averages, width, label = "2017 Base", color = "skyblue")
    else:
        ax.bar(np.arange(1, 6) + width / 2, dict_2035_averages, width, label = "2020 Base", color = "orange")
        
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xticklabels(scenarios)
ax.set_xlabel("Scenario")
ax.set_ylabel("Population Weighted PM2.5 Concentration Mean")
ax.set_title("Population Weighted PM2.5 Concentration Mean Across Scenarios (2035)")
    
plt.legend()
plt.tight_layout()
plt.savefig("Emission Files/2020 to 2030, 2035 Population Weighted PM2.5 Mean/2035 (2020 Pop).png")
plt.show()
    
    
    