'''
Maps each model grid cell to a province/region cluster and population
count, then for every PM2.5 NetCDF file builds a population-weighted
exposure curve (cumulative population % vs. PM2.5 level, colored by
region) and saves it as a PNG per scenario/met-year.
'''

import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from matplotlib.patches import Patch
import numpy as np
from common import build_in_china_mask, get_province_gdf

province_to_region = {
    '北京市': 'BTHS',
    '天津市': 'BTHS',
    '河北省': 'BTHS',
    '山东省': 'BTHS',
    '河南省': 'BTHS',
    '山西省': 'FWP',
    '陕西省': 'FWP',
    '甘肃省': 'FWP',
    '宁夏回族自治区': 'FWP',
    '上海市': 'YRD',
    '江苏省': 'YRD',
    '浙江省': 'YRD',
    '安徽省': 'YRD',
    '四川省': 'SCB',
    '重庆市': 'SCB',
    '广东省': 'PRD',
}

path_nc_files = Path("NC Files and Emission Reports - 2020 to 2030")
nc_files = sorted(path_nc_files.glob("*.nc"))

province_gdf = get_province_gdf()

ds = xr.open_dataset(nc_files[0])
lon_flat = ds["lon"].values.flatten()
lat_flat = ds["lat"].values.flatten()

in_china_flat = build_in_china_mask(ds["lon"].values, ds["lat"].values).flatten()

points_gdf = gpd.GeoDataFrame(
    geometry = [Point(lon, lat) for lon, lat in zip(lon_flat, lat_flat)],
    crs = 'EPSG:4326'
)

joined = gpd.sjoin(points_gdf, province_gdf, how = 'left', predicate = 'within')
joined = joined[['province']]
joined['region'] = joined['province'].map(province_to_region).fillna('Other')

df_population = np.load("Emission Files/pop_grid_wrf_2030.npy")

joined['Population Per Cell'] = df_population.flatten()

joined = joined[in_china_flat]
joined['lon'] = lon_flat[in_china_flat]
joined['lat'] = lat_flat[in_china_flat]
    
region_colors = {
    'BTHS': 'red',
    'FWP': 'orange',
    'YRD': 'green',
    'SCB': 'purple',
    'PRD': 'blue',
    'Other': '#D3D3D3'
}

for file in nc_files:
    print(f"Processing: {file.stem}")
    ds = xr.open_dataset(file)
    
    pm25_data = ds["pred_PM25"].mean(dim = "time").values.flatten()[in_china_flat]
    joined["pm25"] = pm25_data

    plot_df = joined.dropna(subset = ['province']).copy()

    plot_df = plot_df.sort_values('pm25').reset_index(drop = True)

    plot_df['cum_pop'] = plot_df['Population Per Cell'].cumsum()
    plot_df['cum_pop_frac'] = plot_df['cum_pop'] / plot_df['Population Per Cell'].sum() * 100

    total_pop = plot_df['Population Per Cell'].sum()
    plot_df['bar_width'] = plot_df['Population Per Cell'] / total_pop * 100
    
    fig, ax = plt.subplots(figsize = (10, 6))

    plot_df['pop_start'] = plot_df['cum_pop_frac'] - plot_df['bar_width']
    
    for i in range(len(plot_df) - 1):
        x_start = plot_df['pop_start'].iloc[i]
        x_end = plot_df['pop_start'].iloc[i + 1]
        color = region_colors[plot_df['region'].iloc[i]]
        ax.fill_between([x_start, x_end], [plot_df['pm25'].iloc[i], plot_df['pm25'].iloc[i + 1]], color = color, alpha = 0.8)
        
    ax.fill_between([plot_df['pop_start'].iloc[-1], 100], [plot_df['pm25'].iloc[-1], plot_df['pm25'].iloc[-1]],
                    color = region_colors[plot_df['region'].iloc[-1]], alpha = 0.8)

    ax.plot(plot_df['pop_start'], plot_df['pm25'], color = 'black', linewidth = 0.8)
    ax.plot([plot_df.iloc[-1]['pop_start'], 100], [plot_df.iloc[-1]['pm25'], plot_df.iloc[-1]['pm25']], 
            color = 'black', linewidth = 0.8)

    ax.axhline(30, linestyle = '--', color = 'gray', label = '30 μg/m³')
    ax.set_xlabel('Population Fraction (%)')
    ax.set_ylabel('PM2.5 Exposure (μg/m³)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0)
    
    legend_elements = [
        Patch(facecolor = 'red', label = 'Beijing-Tianjin-Hebei and Surroundings'),
        Patch(facecolor = 'orange', label = 'Fenwei Plain'),
        Patch(facecolor = 'green', label = 'Yangtze River Delta'),
        Patch(facecolor = 'purple', label = 'Sichuan Basin'),
        Patch(facecolor = 'blue', label = 'Pearl River Delta'),
        Patch(facecolor = '#D3D3D3', label = 'Other'),
    ]

    ax.legend(handles = legend_elements, loc = 'upper left')
    
    scenario = file.stem.split("_")[0].split("-2030-")[1]
    met_year = file.stem.split("_")[1].split("Met")[0]

    plt.title(f"PM2.5 Population Exposure for {scenario} - {met_year} | 2020 - 2030")
    plt.tight_layout()
    plt.savefig(f"Emission Files/40 Scenario Concentration Maps/{scenario}_{met_year}_exposure_curve_2020-2030.png", dpi = 300)
    plt.close()
    
print("Finished!")
    
    
    
    
    