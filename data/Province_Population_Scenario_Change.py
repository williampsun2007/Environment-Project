import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from cnmaps import get_adm_maps
import geopandas as gpd
import pandas as pd

df = pd.read_csv("Population_Projection/Population_Projection_Data/Province/Pop_TOTAL.csv")
df.dropna(inplace = True)

province_map = {
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

gdf = gpd.GeoDataFrame(records, crs='EPSG:4326')

col_not_2020_2035 = []
for col in df.columns:
    if (col != "V1" and col != "2020" and col != "2035"):
        col_not_2020_2035.append(col)

for fer in range(1, 6):
    for mig in range(1, 4):
        scenario = f"_SSPFer{fer}_SSPMigr{mig}"
        df_scenario = df[df["V2"] == scenario]
        df_scenario = df_scenario.drop(col_not_2020_2035, axis = 1)
        df_scenario['Difference'] = df_scenario["2035"] - df_scenario["2020"]
        
        fig = plt.figure(figsize = (12, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
        norm = mcolors.TwoSlopeNorm(vmin=-15e6, vcenter=0, vmax=15e6)
        cmap = cm.RdYlGn
        
        def get_color(name):
            if name in province_map and name not in ["台湾省", "香港特别行政区", "澳门特别行政区"]:
                rows = df_scenario[df_scenario['V1'] == province_map[name]]
                if not rows.empty:
                    return cmap(norm(rows.iloc[0]['Difference']))
            return 'lightgrey'
        
        gdf['color'] = gdf['province'].apply(get_color)
        gdf.plot(color=gdf['color'], ax=ax, edgecolor='black', linewidth=0.5)
                
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
        cbar.set_label('Population Change 2020–2035')
        cbar.set_ticks([-15e6, -10e6, -5e6, 0, 5e6, 10e6, 15e6])
        cbar.set_ticklabels(['-15M', '-10M', '-5M', '0', '+5M', '+10M', '+15M'])

        plt.title(f"Population Change by Province for Scenario {scenario}")
        plt.savefig(f"Emission Files/15 Scenario Population Province Change/{scenario}_Scenario.png")
        plt.close(fig)

print("Finished!")