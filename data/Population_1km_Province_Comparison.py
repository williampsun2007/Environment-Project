import pandas as pd
import plotly.graph_objects as go

df_1km = pd.read_excel("Population Graph Data/1km_Resolution_Data.xlsx")
df_province = pd.read_excel("Population Graph Data/Province_Resolution_Data.xlsx")

data_cols_1km = [c for c in df_1km.columns if '_' in str(c)]
years_1km = sorted(set(int(c.split('_')[1]) for c in data_cols_1km))

years_province = list(range(2010, 2101))

fig = go.Figure()

province_list = ['Total'] + [p for p in df_1km['Province'].dropna().tolist() if p != 'Total']

scenarios = ["SSP1", "SSP2", "SSP3", "SSP4", "SSP5"]

scenarios_province = ["_SSPFer1_SSPMigr1", "_SSPFer1_SSPMigr2", "_SSPFer1_SSPMigr3",
                      "_SSPFer2_SSPMigr1", "_SSPFer2_SSPMigr2", "_SSPFer2_SSPMigr3",
                      "_SSPFer3_SSPMigr1", "_SSPFer3_SSPMigr2", "_SSPFer3_SSPMigr3",
                      "_SSPFer4_SSPMigr1", "_SSPFer4_SSPMigr2", "_SSPFer4_SSPMigr3",
                      "_SSPFer5_SSPMigr1", "_SSPFer5_SSPMigr2", "_SSPFer5_SSPMigr3"]

scenario_color = {
    "SSP1": "#ffd700", 
    "SSP2": "#ff8c00",  
    "SSP3": "#ff4500", 
    "SSP4": "#dc143c",  
    "SSP5": "#8b0000", 
}

fertility_color = {
    "SSPFer1": "#b3d9ff", 
    "SSPFer2": "#66b2ff", 
    "SSPFer3": "#1a8cff", 
    "SSPFer4": "#0059b3", 
    "SSPFer5": "#002966", 
}

migration_dash = {
    "SSPMigr1": "solid",
    "SSPMigr2": "dash",
    "SSPMigr3": "dot",
}

for idx, province in enumerate(province_list):
    visible = (idx == 0)
    
    for scenario in scenarios:
        total_over_time = []
        for year in years_1km:
            if province == "Total":
                total_pop = df_1km[f"{scenario}_{year}"].sum()
            else:
                total_pop = df_1km[df_1km["Province"] == province].iloc[0][f"{scenario}_{year}"]
            total_over_time.append(total_pop)

        fig.add_trace(go.Scatter(x = years_1km, y = total_over_time, line = dict(color = scenario_color[scenario], width = 2), 
                                 name = f"{scenario}_1km", visible = visible))
        
    for scenario in scenarios_province:
        total_over_time = []
        for year in years_province:
            if province == "Total":
                total_pop = df_province[df_province["V2"] == scenario][str(year)].sum()
            else:
                total_pop = df_province[(df_province["V1"] == province) & (df_province["V2"] == scenario)][str(year)].sum()
            total_over_time.append(total_pop)
        
        fertility = scenario.split("_")[1]
        migration = scenario.split("_")[2]
        
        fig.add_trace(go.Scatter(x = years_province, y = total_over_time, 
                                 line = dict(color = fertility_color[fertility], width = 2, dash = migration_dash[migration]), 
                                 name = f"{fertility[3:]}_{migration[3:]}_province", visible = visible))    
        
traces_per_province = 20
buttons = []
for idx, province in enumerate(province_list):
    visibility = [False] * len(fig.data)
    start = idx * traces_per_province
    for t in range(traces_per_province):
        visibility[start + t] = True
    buttons.append(dict(label = province, method = 'update',
        args = [{'visible': visibility}, {'title': f'{province} Population Projection - Scenarios Across Province and 1km Datasets'}]))
    
fig.update_layout(
    updatemenus = [dict(buttons = buttons, direction = 'down', x = 0.1, y = 1.15)],
    title = f'{province_list[0]} Population Projection',
    xaxis_title = 'Year',
    yaxis_title = 'Population'
)

fig.write_html("Population Graph Data/1km_and_Province_Datasets_Projections.html")
fig.show()
