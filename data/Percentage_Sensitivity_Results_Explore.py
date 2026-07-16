from pathlib import Path
import zipfile
import netCDF4 as nc
import geopandas as gpd
from shapely.vectorized import contains
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

dictionary = {}

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

for folder in Path("Scenario Percentage Decrease Downloads").iterdir():
    if not zipfile.is_zipfile(folder):
        nc_files = Path(folder).glob("*.nc")
        for file in nc_files:
            name = file.stem
            parts = name.split("_")
            scenario = f"{parts[1]}_{parts[2]}"
            
            ds = xr.open_dataset(file)
            data = ds["pred_PM25"].mean(dim = "time").values
    
            data[~in_china] = 0
            
            above_25 = (data >= 25)
    
            pct = pop_china_2020[above_25].sum() / total_pop * 100
    
            if dictionary.get(scenario) is None:
                dictionary[scenario] = []
        
            dictionary[scenario].append(pct)
            
colors = {"SO2": "green", "NOX": "blue", "NH3": "orange", "VOC": "purple", "PM": "red"}
            
fig, ax = plt.subplots(figsize = (12, 7))
for pollutant in ["SO2", "NOX", "NH3", "VOC", "PM"]:
    results = []
    for pct in range(10, 101, 10):
        scenario = dictionary[f"{pollutant}_{pct}pct"]
        results.append(np.mean(scenario))
        print(f"Scenario: {pollutant}_{pct}pct, Mean: {np.mean(scenario)}")
        
    ax.plot(list(range(10, 101, 10)), results, color = colors[pollutant], label = pollutant, marker = 'o', linestyle = "--")
    
fig.legend()
ax.set_title("Percentage of Chinese Population Above 25 ug/m3 PM2.5 Concentration")
ax.set_xlabel("Percent Reduction")
ax.set_ylabel("Percentage of Chinese Population (%)")
plt.tight_layout(rect = [0, 0, 0.88, 1])

plt.savefig("Emission Files/Percentage Reduction Sensitivity Figures/population_above_25.png")
plt.show()
        
    