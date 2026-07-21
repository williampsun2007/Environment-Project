'''
For each of the 15 fertility x migration scenarios, computes 2020->
2035 population % change per province and plots a choropleth map,
saving one PNG per scenario.
'''

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd
from common import PROVINCE_MAP_POPULATION, EXCLUDED_REGIONS, get_province_gdf

df = pd.read_csv("Population_Projection/Population_Projection_Data/Province/Pop_TOTAL.csv")
df.dropna(inplace = True)

gdf = get_province_gdf()

col_not_2020_2035 = []
for col in df.columns:
    if (col != "V1" and col != "2020" and col != "2035"):
        col_not_2020_2035.append(col)

for fer in range(1, 6):
    for mig in range(1, 4):
        scenario = f"_SSPFer{fer}_SSPMigr{mig}"
        df_scenario = df[df["V2"] == scenario]
        df_scenario = df_scenario.drop(col_not_2020_2035, axis = 1)
        df_scenario['Percent Change'] = ((df_scenario["2035"] - df_scenario["2020"]) / df_scenario["2020"]) * 100
        
        fig = plt.figure(figsize = (12, 10))
        ax = plt.axes(projection = ccrs.PlateCarree())
        norm = mcolors.TwoSlopeNorm(vmin = -25, vcenter = 0, vmax = 25)
        cmap = cm.RdYlGn
        
        def get_color(name):
            if name in PROVINCE_MAP_POPULATION and name not in EXCLUDED_REGIONS:
                rows = df_scenario[df_scenario['V1'] == PROVINCE_MAP_POPULATION[name]]
                if not rows.empty:
                    return cmap(norm(rows.iloc[0]['Percent Change']))
            return 'lightgrey'
        
        gdf['color'] = gdf['province'].apply(get_color)
        gdf.plot(color = gdf['color'], ax = ax, edgecolor = 'black', linewidth = 0.5)
                
        sm = cm.ScalarMappable(cmap = cmap, norm = norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax = ax, orientation = 'vertical', pad = 0.02)
        cbar.set_label('Population Percent Change from 2020 to 2035')
        cbar.set_ticks([-25, -15, -5, 0, 5, 15, 25])
        cbar.set_ticklabels(['-25%', '-15%', '-5%', '0', '5%', '15%', '25%'])

        plt.title(f"Population Percent Change by Province for Scenario {scenario} from 2020 to 2035")
        plt.savefig(f"Emission Files/15 Scenario Population Percent Change/{scenario}_Scenario.png")
        plt.close(fig)

print("Finished!")