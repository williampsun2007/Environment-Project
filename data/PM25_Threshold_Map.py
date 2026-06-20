import xarray as xr
import geopandas as gpd
import shapely
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig = plt.figure(figsize = (15, 12))
ax = plt.axes(projection = ccrs.PlateCarree())

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

ds = xr.open_dataset("2020_Base_Data/PM25.nc")

lon_flat = ds["lon"].values.flatten()
lat_flat = ds["lat"].values.flatten()

in_china_flat = shapely.contains_xy(china.geometry.iloc[0], lon_flat, lat_flat)
in_china = in_china_flat.reshape(ds["lon"].shape)

data = ds["pred_PM25"].mean(dim = "time").values.copy()

colors_map = np.where(data >= 35, 1, 0)
colors_map = np.where(in_china, colors_map, np.nan)

provinces = cfeature.NaturalEarthFeature(
    category = 'cultural',
    name = 'admin_1_states_provinces_lines',
    scale = '50m',
    facecolor = 'none'
)

ax.pcolormesh(ds["lon"], ds["lat"], colors_map, cmap = 'coolwarm', vmin = 0, vmax = 1)
ax.coastlines()
ax.add_feature(cfeature.BORDERS)
ax.add_feature(provinces, edgecolor = 'black', linewidth = 0.5)

plt.title("China PM2.5 2020: Red = ≥35, Blue = <35")
plt.savefig("2020_Base_Data/Area over 35.png")
plt.show()
