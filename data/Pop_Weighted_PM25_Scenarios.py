from pathlib import Path
import matplotlib.pyplot as plt
import netCDF4 as nc
import geopandas as gpd
from shapely.vectorized import contains
import numpy as np
import xarray as xr

ds = nc.Dataset("2017_Base_Data/PM25.nc")

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

lon_flat = ds["lon"][:].flatten()
lat_flat = ds["lat"][:].flatten()

in_china_flat = contains(china.geometry.iloc[0], lon_flat, lat_flat)

in_china = in_china_flat.reshape(ds["lon"].shape)

pop_grid_2020 = np.load("Emission Files/pop_grid_wrf_2020.npy")
pop_china_2020 = pop_grid_2020.copy()
pop_china_2020 = np.nan_to_num(pop_china_2020, nan = 0.0)
pop_china_2020[~in_china] = 0
total_pop = pop_china_2020.sum()

scenarios = ["Baseline", "CleanAir", "OTPCA", "OTPNZCA", "EPNZCA"]

nc_files_2030 = Path("NC Files and Emission Reports - 2020 to 2030").glob("*.nc")
dict_2030 = {}
for file in nc_files_2030:
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
    
fig, ax = plt.subplots(figsize = (10, 6))
ax.bar(scenarios, dict_2030_averages)
ax.set_xlabel("Scenario")
ax.set_ylabel("Population Weighted PM2.5 Concentration Mean")
ax.set_title("Population Weighted PM2.5 Concentration Mean Across Scenarios (2020 - 2030)")
plt.tight_layout()
plt.savefig("Emission Files/2020 to 2030, 2035 Population Weighted PM2.5 Mean/2020-2030 (2020 Pop).png")
plt.show()

nc_files_2035 = Path("NC Files and Emission Reports - 2020 to 2035").glob("*.nc")
dict_2035 = {}
for file in nc_files_2035:
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
    
fig, ax = plt.subplots(figsize = (10, 6))
ax.bar(scenarios, dict_2035_averages)
ax.set_xlabel("Scenario")
ax.set_ylabel("Population Weighted PM2.5 Concentration Mean")
ax.set_title("Population Weighted PM2.5 Concentration Mean Across Scenarios (2020 - 2035)")
plt.tight_layout()
plt.savefig("Emission Files/2020 to 2030, 2035 Population Weighted PM2.5 Mean/2020-2035 (2020 Pop).png")
plt.show()
    
    
    