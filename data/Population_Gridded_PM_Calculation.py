import rasterio
import rasterio.windows
import netCDF4 as nc
import numpy as np
import xarray as xr
import geopandas as gpd
from shapely.vectorized import contains
 
TIF_PATH = "Population Projection Gridded/Adj_2015_Int.tif"           
OUT_PATH = "2017_Base_Data/pop_grid_wrf_2017.npy"                       
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
print(f"Shape        : {pop_grid.shape}")
print(f"Valid cells  : {np.sum(~np.isnan(pop_grid))}")
print(f"Total pop    : {np.nansum(pop_grid):,.0f}")
print(f"Max cell pop : {np.nanmax(pop_grid):,.0f}")

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

lon_flat = ds["lon"][:].flatten()
lat_flat = ds["lat"][:].flatten()

in_china_flat = contains(china.geometry.iloc[0], lon_flat, lat_flat)

in_china = in_china_flat.reshape(ds["lon"].shape)

pop_grid_2017 = np.load("2017_Base_Data/pop_grid_wrf_2017.npy")
pop_china_2017 = pop_grid_2017.copy()
pop_china_2017 = np.nan_to_num(pop_china_2017, nan = 0.0)

ds_2017_baseline = xr.open_dataset("2017_Base_Data/PM25.nc")
data = ds_2017_baseline["pred_PM25"].mean(dim = "time").values

above_25 = (data >= 25)
mask = in_china & above_25

print(pop_china_2017[mask].sum() / pop_china_2017[in_china].sum())
print(pop_china_2017[mask].sum())
print(pop_china_2017[in_china].sum())