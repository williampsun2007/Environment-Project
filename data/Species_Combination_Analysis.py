'''
For each pollutant-combination scenario file (binary code decoded to
a pollutant list), computes the 2020-population-weighted mean PM2.5
and the % of population exposed above 25 ug/m3, and saves the
results to a summary workbook.
'''

from pathlib import Path
import openpyxl
import numpy as np
import netCDF4 as nc
import geopandas as gpd
from shapely.vectorized import contains
import xarray as xr

folder = Path("Species Combination Test Downloads/Batch1, 7-10-2026")
nc_files = folder.glob("*nc")

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

wb = openpyxl.Workbook()
ws = wb.active

for file in nc_files:
    parts = file.stem.split("_")
    binary_code = parts[2]
    pollutants = ""
    species = ["SO2", "NOx", "NH3", "VOC", "PM"]
    for i in range(0, 5):
        if (binary_code[i] == "1"):
            if (pollutants == ""):
                pollutants += species[i]
            else:
                pollutants += f"+{species[i]}"
                
    ds = xr.open_dataset(file)
    data = ds["pred_PM25"].mean(dim = "time").values
    data[~in_china] = 0
            
    above_25 = (data >= 25)
    pct = pop_china_2020[above_25].sum() / total_pop * 100
    
    multiplied = data * pop_china_2020
    mean_pm = multiplied.sum() / total_pop
    
    ws.append([pollutants, parts[3].split("Met")[0], mean_pm, pct])
    
wb.save("Emission Files/EPNZCA Species Combination Analysis/mean-pm_pct-pop_2020-pop.xlsx")