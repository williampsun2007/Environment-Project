import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs
import xarray as xr
import geopandas as gpd
import shapely
import cartopy.feature as cfeature

pop_grid_2035 = np.load("Emission Files/pop_grid_wrf_2035.npy")

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

ds = xr.open_dataset("2020_Base_Data/PM25.nc")

lon_flat = ds["lon"].values.flatten()
lat_flat = ds["lat"].values.flatten()

in_china_flat = shapely.contains_xy(china.geometry.iloc[0], lon_flat, lat_flat)
in_china = in_china_flat.reshape(ds["lon"].shape)

pop_grid_2035[pop_grid_2035 == 0] = 1
pop_grid_2035[~in_china] = np.nan

provinces = cfeature.NaturalEarthFeature(
    category = 'cultural',
    name = 'admin_1_states_provinces_lines',
    scale = '50m',
    facecolor = 'none'
)

nc_files = sorted(Path("NC Files and Emission Reports - 2017 to 2035").glob("*.nc"))
for file in nc_files:
    pm25 = xr.open_dataset(file)["pred_PM25"].mean(dim = "time").values
    
    fig = plt.figure(figsize = (18, 10))
    ax = fig.add_axes([0.05, 0.05, 0.75, 0.9], projection = ccrs.PlateCarree())
    
    cmap_gray = LinearSegmentedColormap.from_list('custom_grays', ['#f0f0f0', '#1a1a1a'])
    cmap_gray.set_bad(alpha = 0)
    norm_gray = PowerNorm(gamma = 0.5, vmin = 1, vmax = 5_000_000)

    cmap_red = LinearSegmentedColormap.from_list('custom_reds', ['#ffcccc', '#8b0000'])
    cmap_red.set_bad(alpha = 0)
    norm_red = PowerNorm(gamma = 0.5, vmin = 1, vmax = 5_000_000)

    below_25_pop = np.where((pm25 < 25) & in_china, pop_grid_2035, np.nan)
    above_25_pop = np.where((pm25 >= 25) & in_china, pop_grid_2035, np.nan)

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
    
    parts = file.stem.split("-2035-")
    scenario = parts[1].split("-2017-")[0]
    year = parts[1].split("-2017-")[1].split("_")[0]
    
    ax.set_title(
        f"China Population Distribution by PM2.5 Exposure (2035)\n"
        f"Gray: < 25 µg/m³ | Red: ≥ 25 µg/m³ | Color Intensity = Population Density\n"
        f"Scenario: {scenario} | Met Year: {year}",
        fontsize = 10
    )
    
    plt.tight_layout(rect = [0, 0, 0.85, 0.95])
    plt.savefig(f"Emission Files/2017-2035 Scenario Threshold Pop. Maps/{scenario}_{year}.png")
    plt.close()
    
print("Finished!")
    
    
    
    
    
