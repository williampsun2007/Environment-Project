import rasterio
import rasterio.windows
import netCDF4 as nc
import numpy as np
import xarray as xr
import geopandas as gpd
from shapely.vectorized import contains
from pathlib import Path
import openpyxl
 
TIF_PATH = "Population Projection Gridded/ChinaPopSSP2Int/Adj_SSP2_2030Int.tif"           
OUT_PATH = "Emission Files/pop_grid_wrf_2030.npy"                       
HALF_WRF_DEG = 0.18
 
ds = nc.Dataset("2017_Base_Data/PM25.nc")
lat = ds.variables["lat"][:]   # shape (127, 172)
lon = ds.variables["lon"][:]   # shape (127, 172)
ny, nx = lat.shape
 
pop_grid = np.full((ny, nx), np.nan, dtype = np.float64)
 
with rasterio.open(TIF_PATH) as src:
    nodata = src.nodata
 
    for i in range(ny):
        for j in range(nx):
            clat = float(lat[i, j])
            clon = float(lon[i, j])
 
            left = clon - HALF_WRF_DEG
            right = clon + HALF_WRF_DEG
            bottom = clat - HALF_WRF_DEG
            top = clat + HALF_WRF_DEG
 
            row_start, col_start = src.index(left, top)
            row_stop,  col_stop  = src.index(right, bottom)
 
            row_start = max(0, row_start)
            col_start = max(0, col_start)
            row_stop  = min(src.height, row_stop)
            col_stop  = min(src.width,  col_stop)
 
            if row_stop <= row_start or col_stop <= col_start:
                continue
 
            window = rasterio.windows.Window(
                col_start, row_start,
                col_stop - col_start,
                row_stop - row_start,
            )
            
            data = src.read(1, window = window).astype(np.float64)
            data[data == nodata] = np.nan
 
            valid = data[~np.isnan(data)]
            if len(valid) > 0:
                pop_grid[i, j] = valid.sum()
 
        if i % 20 == 0:
            print(f"  Row {i}/{ny} complete…")
            
np.save(OUT_PATH, pop_grid)
            
world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

lon_flat = ds["lon"][:].flatten()
lat_flat = ds["lat"][:].flatten()

in_china_flat = contains(china.geometry.iloc[0], lon_flat, lat_flat)

in_china = in_china_flat.reshape(ds["lon"].shape)

pop_grid_2030 = np.load("Emission Files/pop_grid_wrf_2030.npy")
pop_china_2030 = pop_grid_2030.copy()
pop_china_2030 = np.nan_to_num(pop_china_2030, nan = 0.0)
            
wb = openpyxl.Workbook()
sheet = wb.active
            
nc_files = sorted(Path("NC Files and Emission Reports - 2020 to 2030 Scenarios").glob("*.nc"))
for file in nc_files:
    ds_2030 = xr.open_dataset(file)
    data = ds_2030["pred_PM25"].mean(dim = "time").values
    
    above_35 = (data >= 35)
    mask = in_china & above_35
    
    print(f"{file.stem}: {data[in_china].mean()}")
    
    percentage = (pop_china_2030[mask].sum() / pop_china_2030[in_china].sum()) * 100
    
    parts = file.stem.split("_")
    scenario = parts[0]
    year = parts[1].split("Met")[0]
    
    sheet.append([scenario, year, percentage])
    
wb.save("Emission Files/2030 Scenarios above 35 Pop. Percentage.xlsx")
print("Finished!")