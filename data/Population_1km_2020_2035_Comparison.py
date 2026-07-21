'''
Loads 1km-resolution 2020/2035 population rasters for the SSP5
scenario, sums each by province, and plots a choropleth of absolute
population change per province, saving the figure.
'''

import geopandas as gpd
from cnmaps import get_adm_maps
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.colors as mcolors
import matplotlib.cm as cm

with rasterio.open("Population Projection Gridded 2/SSP5RCP4_5/grid_pop_count2020_SSP5_RCP4_5.tif") as src:
    pop_1km_2020 = src.read(1).astype('float64')
    transform = src.transform
    nodata = src.nodata
    shape = pop_1km_2020.shape
    crs = src.crs

with rasterio.open("Population Projection Gridded 2/SSP5RCP4_5/grid_pop_count2035_SSP5_RCP4_5.tif") as src:
    pop_1km_2035 = src.read(1).astype('float64')
    transform = src.transform
    nodata = src.nodata
    shape = pop_1km_2035.shape
    crs = src.crs
    
pop_1km_2020[pop_1km_2020 == nodata] = 0
pop_1km_2035[pop_1km_2035 == nodata] = 0

province_map = gpd.read_file("https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json")
province_map = province_map[['name', 'geometry']].rename(columns = {'name': 'province'})

province_map['id'] = range(1, len(province_map) + 1)
id_to_province = dict(zip(province_map['id'], province_map['province']))

province_raster = np.load("Population Projection Gridded 2/Province Rasters/province_raster_2035_ssp5.npy")

fig = plt.figure(figsize = (12, 10))
ax = plt.axes(projection = ccrs.PlateCarree())
norm = mcolors.TwoSlopeNorm(vmin = -10000000, vcenter = 0, vmax = 10000000)
cmap = cm.RdYlGn

def get_difference(x):
    prov_mask = province_raster == x
    total_2020 = pop_1km_2020[prov_mask].sum()
    total_2035 = pop_1km_2035[prov_mask].sum()
    return total_2035 - total_2020

province_map['difference'] = province_map['id'].apply(get_difference)
province_map['color'] = province_map['difference'].apply(lambda x: cmap(norm(x)))

province_map.plot(color = province_map['color'], ax = ax, edgecolor = 'black', linewidth = 0.5)
sm = cm.ScalarMappable(cmap = cmap, norm = norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax = ax, orientation = 'vertical', pad = 0.02)
cbar.set_label('Population Change from 2020 to 2035 - 1km Dataset')
cbar.set_ticks([-10000000, -5000000, 0, 5000000, 10000000])
cbar.set_ticklabels(['-10M', '-5M', '0', '5M', '10M'])

print(province_map['difference'].min())
print(province_map['difference'].max())

plt.title(f"Population Absolute Change by Province for Scenario SSP5 from 2020 to 2035 - 1km Dataset")
plt.savefig(f"Emission Files/15 Scenario Population Absolute Change - 1km Dataset/SSP5_Scenario.png")
plt.close(fig)