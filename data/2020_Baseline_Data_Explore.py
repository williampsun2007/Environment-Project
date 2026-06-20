import xarray as xr
from cnmaps import get_adm_maps
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import shapely

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

records = []
for province in get_adm_maps(level='省'):
    records.append({
        'province': province['province'],
        'geometry': province['geometry']
    })

province_map = gpd.GeoDataFrame(records, crs='EPSG:4326')

ds = xr.open_dataset("2020_Base_Data/PM25.nc")
lon_flat = ds["lon"].values.flatten()
lat_flat = ds["lat"].values.flatten()

world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']
in_china_flat = shapely.contains_xy(china.geometry.iloc[0], lon_flat, lat_flat)

points_gdf = gpd.GeoDataFrame(
    geometry=[Point(lon, lat) for lon, lat in zip(lon_flat, lat_flat)],
    crs='EPSG:4326'
)

points_gdf = points_gdf[in_china_flat]
lon_flat = lon_flat[in_china_flat]
lat_flat = lat_flat[in_china_flat]

joined = gpd.sjoin(points_gdf, province_map, how='left', predicate='within')
joined = joined[['province']]
joined['lon'] = lon_flat
joined['lat'] = lat_flat

amount_grid_province = joined.groupby('province')['lat'].count()

df_population = pd.read_csv("Population_Projection/Population_Projection_Data/Province/POP_TOTAL.csv")
df_population = df_population.dropna()
df_population = df_population[df_population["V2"] == "_SSPFer2_SSPMigr3"]

drop_cols = []
for col in df_population.columns:
    if (col != "V1" and col != "2020"):
        drop_cols.append(col)
        
df_population.drop(drop_cols, axis = 1, inplace = True)
df_population = df_population.set_index("V1")

print("Here!!!")

pm25_data = ds["pred_PM25"].mean(dim = "time").values.flatten()[in_china_flat]
joined["pm25"] = pm25_data
joined = joined.dropna(subset = ["province"])

joined["Province Population"] = joined["province"].apply(lambda x: df_population.loc[province_dict[x]]["2020"] if pd.notna(x) else 0)
joined["Population Per Cell"] = joined.apply(
    lambda x: x["Province Population"] / amount_grid_province.loc[x["province"]] if pd.notna(x["province"]) else 0, axis=1
)

pop_in_35 = joined[joined["pm25"] >= 35]["Population Per Cell"].sum()
total_pop = joined["Population Per Cell"].sum()
ratio = pop_in_35 / total_pop

print(f"Population in 35 or higher: {pop_in_35}")
print(f"Total Population: {total_pop}")
print(f"Ratio: {ratio}")
    
    
    
    
    