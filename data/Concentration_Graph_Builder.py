import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
from cnmaps import get_adm_maps
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import shapely
from matplotlib.patches import Patch

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

province_dict = {
    "北京市": "Beijing",
    "天津市": "Tianjin",
    "河北省": "Hebei",
    "山西省": "Shanxi",
    "内蒙古自治区": "NeiMonggol",
    "辽宁省": "Liaoning",
    "吉林省": "Jilin",
    "黑龙江省": "Heilongjiang",
    "上海市": "Shanghai",
    "江苏省": "Jiangsu",
    "浙江省": "Zhejiang",
    "安徽省": "Anhui",
    "福建省": "Fujian",
    "江西省": "Jiangxi",
    "山东省": "Shandong",
    "河南省": "Henan",
    "湖北省": "Hubei",
    "湖南省": "Hunan",
    "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi",
    "海南省": "Hainan",
    "重庆市": "Chongqing",
    "四川省": "Sichuan",
    "贵州省": "Guizhou",
    "云南省": "Yunan",
    "西藏自治区": "Xizang",
    "陕西省": "Shaanxi",
    "甘肃省": "Gansu",
    "青海省": "Qinghai",
    "宁夏回族自治区": "Ningxia",
    "新疆维吾尔自治区": "Xinjiang"
}

path_nc_files = Path("NC Files and Emission Reports")
nc_files = sorted(path_nc_files.glob("*.nc"))

records = []
for province in get_adm_maps(level = '省'):
    records.append({
        'province': province['province'],
        'geometry': province['geometry']
    })

province_map = gpd.GeoDataFrame(records, crs = 'EPSG:4326')

ds = xr.open_dataset(nc_files[0])
lon_flat = ds["lon"].values.flatten()
lat_flat = ds["lat"].values.flatten()

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']
in_china_flat = shapely.contains_xy(china.geometry.iloc[0], lon_flat, lat_flat)

points_gdf = gpd.GeoDataFrame(
    geometry = [Point(lon, lat) for lon, lat in zip(lon_flat, lat_flat)],
    crs = 'EPSG:4326'
)

points_gdf = points_gdf[in_china_flat]
lon_flat = lon_flat[in_china_flat]
lat_flat = lat_flat[in_china_flat]

joined = gpd.sjoin(points_gdf, province_map, how = 'left', predicate = 'within')
joined = joined[['province']]
joined['region'] = joined['province'].map(province_to_region).fillna('Other')
joined['lon'] = lon_flat
joined['lat'] = lat_flat

amount_grid_province = joined.groupby('province')['lat'].count()

df_population = pd.read_csv("Population_Projection/Population_Projection_Data/Province/POP_TOTAL.csv")
df_population = df_population.dropna()
df_population = df_population[df_population["V2"] == "_SSPFer2_SSPMigr3"]

drop_cols = []
for col in df_population.columns:
    if (col != "V1" and col != "2035"):
        drop_cols.append(col)
        
df_population.drop(drop_cols, axis = 1, inplace = True)
df_population = df_population.set_index("V1")

joined["Province Population"] = joined["province"].apply(lambda x: df_population.loc[province_dict[x]]["2035"] if pd.notna(x) else 0)
joined["Population Per Cell"] = joined[["province", "Province Population"]].apply(
    lambda x: x[1] / amount_grid_province.loc[x[0]] if pd.notna(x[0]) else 0, axis=1
)

region_colors = {
    'BTHS': 'red',
    'FWP': 'orange',
    'YRD': 'green',
    'SCB': 'purple',
    'PRD': 'blue',
    'Other': '#D3D3D3'
}

for file in nc_files:
    ds = xr.open_dataset(file)
    
    pm25_data = ds["pred_PM25"].mean(dim="time").values.flatten()[in_china_flat]
    joined["pm25"] = pm25_data

    plot_df = joined.dropna(subset=['province']).copy()

    plot_df = plot_df.sort_values('pm25').reset_index(drop=True)

    plot_df['cum_pop'] = plot_df['Population Per Cell'].cumsum()
    plot_df['cum_pop_frac'] = plot_df['cum_pop'] / plot_df['Population Per Cell'].sum() * 100

    total_pop = plot_df['Population Per Cell'].sum()
    plot_df['bar_width'] = plot_df['Population Per Cell'] / total_pop * 100
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(plot_df['cum_pop_frac'], plot_df['pm25'], color='#D3D3D3', step='post')

    region_df = plot_df[plot_df['region'] != 'Other']
    ax.bar(region_df['cum_pop_frac'], region_df['pm25'], color=region_df['region'].map(region_colors), 
           width=region_df['bar_width'], align='edge', linewidth=0)

    ax.plot(plot_df['cum_pop_frac'], plot_df['pm25'], color='black', linewidth=0.5)

    ax.axhline(25, linestyle='--', color='gray', label='25 μg/m³')

    ax.set_xlabel('Population Fraction (%)')
    ax.set_ylabel('PM2.5 Exposure (μg/m³)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0)

    legend_elements = [
        Patch(facecolor='red', label='Beijing-Tianjin-Hebei and Surroundings'),
        Patch(facecolor='orange', label='Fenwei Plain'),
        Patch(facecolor='green', label='Yangtze River Delta'),
        Patch(facecolor='purple', label='Sichuan Basin'),
        Patch(facecolor='blue', label='Pearl River Delta'),
        Patch(facecolor='#D3D3D3', label='Other'),
    ]

    ax.legend(handles=legend_elements, loc='upper left')

    plt.title(f"PM2.5 Population Exposure for Scenario {file.stem}")
    plt.tight_layout()
    plt.savefig(f"Emission Files/40 Scenario Concentration Maps/{file.stem}_exposure_curve.png", dpi=300)
    
print("Finished!")
    
    
    
    
    