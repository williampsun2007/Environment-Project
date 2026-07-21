'''
Builds an interactive Plotly chart of population projections under
the 5 SSP scenarios (1km-resolution dataset), with a per-province
dropdown, and saves it as a standalone HTML file.
'''

import pandas as pd
import plotly.graph_objects as go

df_1km = pd.read_excel("Population Graph Data/1km_Resolution_Data.xlsx")

data_cols_1km = [c for c in df_1km.columns if '_' in str(c)]
years_1km = sorted(set(int(c.split('_')[1]) for c in data_cols_1km))

fig = go.Figure()

province_list = ['Total'] + [p for p in df_1km['Province'].dropna().tolist() if p != 'Total']

scenarios = ["SSP1", "SSP2", "SSP3", "SSP4", "SSP5"]

scenario_color = {"SSP1": "red", "SSP2": "orange", "SSP3": "green", "SSP4": "blue", "SSP5": "purple"}

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
                                 name = f"{province}_{scenario}", visible = visible))
        
traces_per_province = 5
buttons = []
for idx, province in enumerate(province_list):
    visibility = [False] * len(fig.data)
    start = idx * traces_per_province
    for t in range(traces_per_province):
        visibility[start + t] = True
    buttons.append(dict(label = province, method = 'update',
        args = [{'visible': visibility}, {'title': f'{province} Population Projection - 1km Dataset - 5 SSP Scenarios'}]))
    
fig.update_layout(
    updatemenus = [dict(buttons = buttons, direction = 'down', x = 0.1, y = 1.15)],
    title = f'{province_list[0]} Population Projection',
    xaxis_title = 'Year',
    yaxis_title = 'Population'
)

fig.write_html("Population Graph Data/1km_dataset_ssp_projections.html")
fig.show()
