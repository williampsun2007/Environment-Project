"""
Reads the 155 province×species perturbation runs (EPNZCA 2035 floor, one
province's one species cut an extra 10%, met 2020 pilot), differences each
against the EPNZCA reference, applies population weighting, and outputs a
sorted leverage table on BOTH objectives (pop-weighted mean PM2.5, and
% population > 25 ug/m3). Also prints the wide-vs-narrow diagnostic that
decides whether the near-optimal manifold is worth optimizing over.
"""

import numpy as np
import pandas as pd
import netCDF4 as nc
import xarray as xr
from pathlib import Path
from common import PROVINCE_ARR, build_in_china_mask

ds = nc.Dataset("2017_Base_Data/PM25.nc")

in_china = build_in_china_mask(ds["lon"][:], ds["lat"][:])

pollutants = ["SO2", "NOx", "NH3", "VOC", "PM25"]

pop_grid_2020 = np.load("Emission Files/pop_grid_wrf_2020.npy")
pop_china_2020 = pop_grid_2020.copy()
pop_china_2020 = np.nan_to_num(pop_china_2020, nan = 0.0)
pop_china_2020[~in_china] = 0
total_pop = pop_china_2020.sum()

folder = Path("NC Files and Emission Reports - OP1 Scenarios")
nc_files = folder.glob("*.nc")

province_col = []
species_col = []
new_pm25_avg_col = []
new_pct_above_25_col = []
pm25_change = []
pct_change = []

data_epnzca_base = xr.open_dataset("NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_early-peak-net-zero-clean-air_2020Met.nc")["pred_PM25"].mean(dim = "time").values
data_epnzca_base[~in_china] = 0
mean_pm25_pop_base = (data_epnzca_base * pop_china_2020).sum() / pop_china_2020.sum()

above_25_base = (data_epnzca_base >= 25)
pct_base = pop_china_2020[above_25_base].sum() / total_pop * 100

species_dict = {"SO2": [], "NOx": [], "NH3": [], "VOC": [], "PM25": []}

for file in nc_files:
    parts = file.stem.split("_")
    province = PROVINCE_ARR[int(parts[3][2:]) - 1]
    species = pollutants[int(parts[4][2:]) - 1]
    
    data = xr.open_dataset(file)["pred_PM25"].mean(dim = "time").values
    
    data[~in_china] = 0
    mean_pm25_pop = (data * pop_china_2020).sum() / pop_china_2020.sum()

    above_25 = (data >= 25)
    pct = pop_china_2020[above_25].sum() / total_pop * 100
    
    province_col.append(province)
    species_col.append(species)
    new_pm25_avg_col.append(mean_pm25_pop)
    new_pct_above_25_col.append(pct)
    pm25_change.append(mean_pm25_pop_base - mean_pm25_pop)
    pct_change.append(pct_base - pct)
    
    species_dict[species].append(mean_pm25_pop_base - mean_pm25_pop)

df_results = pd.DataFrame({"Province": province_col, "Species": species_col, "New PM2.5 Pop-Weighted Mean": new_pm25_avg_col, "New % Pop > 25 ug/m3": new_pct_above_25_col, 
                           "Reduction in PM2.5 Pop-Weighted Mean from Base": pm25_change, "Reduction in % Pop > 25 ug/m3 from Base": pct_change})

df_results.to_csv("Emission Files/OP1 Scenario Analysis/OP1_Leverage_Table.csv", index = False)

df_results = df_results.sort_values("Reduction in PM2.5 Pop-Weighted Mean from Base", ascending = False)
df_results.to_csv("Emission Files/OP1 Scenario Analysis/OP1_Leverage_Table_Sorted.csv", index = False)

print(f"Baseline EPNZCA 2035 Pop-Weighted Mean PM2.5: {mean_pm25_pop_base:.3f} ug/m3")
print(f"Baseline EPNZCA 2035 % Pop > 25 ug/m3: {pct_base:.2f}%")
print("----------------------")

df_results_top = df_results.head(30)
print(f"Top 30 Scenarios by PM2.5 Reduction:")
print(df_results_top)
print("----------------------")

top10_pm25_provinces = df_results.sort_values("Reduction in PM2.5 Pop-Weighted Mean from Base", ascending = False)["Province"].head(10).tolist()
top10_pct_provinces = df_results.sort_values("Reduction in % Pop > 25 ug/m3 from Base", ascending = False)["Province"].head(10).tolist()
overlap = set(top10_pm25_provinces) & set(top10_pct_provinces)
print(f"Provinces in top 10 of both objectives: {overlap}")

if (len(overlap) == 0):
    print("No provinces are in the top 10 of both objectives")
print("----------------------")

for species, list in species_dict.items():
    list_sorted = sorted(list, reverse = True)
    greatest_lever = list_sorted[0]
    tenth_lever = list_sorted[9]
    ratio = greatest_lever / tenth_lever if tenth_lever > 1e-9 else float("inf")
    print(f"Species: {species}, Greatest Lever: {greatest_lever:.3f}, 10th Lever: {tenth_lever:.3f}, Ratio: {ratio:.3f}")
print("----------------------")


