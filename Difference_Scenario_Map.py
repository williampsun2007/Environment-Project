import xarray as xr
import geopandas as gpd
import shapely
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig = plt.figure(figsize=(15, 12))
ax = plt.axes(projection=ccrs.PlateCarree())

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

ds_ontime = xr.open_dataset(r"C:\Users\sunyi\Environment_Project\NC Files and Emission Reports\EmissionReductions2035_on-time-peak-clean-air_2024Met.nc")
ds_earlypeak = xr.open_dataset(r"C:\Users\sunyi\Environment_Project\NC Files and Emission Reports\EmissionReductions2035_early-peak-net-zero-clean-air_2024Met.nc")

lon_flat = ds_ontime["lon"].values.flatten()
lat_flat = ds_ontime["lat"].values.flatten()

in_china_flat = shapely.contains_xy(china.geometry.iloc[0], lon_flat, lat_flat)
in_china = in_china_flat.reshape(ds_ontime["lon"].shape)
        
difference = ds_ontime["pred_PM25"].mean(dim="time").values.copy() - ds_earlypeak["pred_PM25"].mean(dim="time").values.copy()
difference[~in_china] = np.nan

min_value = np.nanmin(difference)
max_value = np.nanmax(difference)

im = ax.pcolormesh(ds_ontime["lon"], ds_ontime["lat"], difference, vmin=min(min_value, -max_value), vmax=max(-min_value, max_value))

ax.coastlines()
ax.add_feature(cfeature.BORDERS)

plt.title("Difference in PM2.5 Concentration from OPTCA to EPNZCA Scenarios throughout China, 2024 Met Year")
plt.colorbar(im, label="PM2.5 Concentration Decrease from OTPCA to EPNZCA")
plt.savefig(r"C:\Users\sunyi\Environment_Project\Emission Files\PM2.5_Difference_OTPCA_to_EPNZCA_2024Met.png")
plt.show()

