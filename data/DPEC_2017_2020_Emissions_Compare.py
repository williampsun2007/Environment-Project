'''
Builds an interactive 5x5 Plotly grid (pollutant x scenario) of bar
charts comparing DPEC/2017-base/2020-base emissions with a 2030
marker overlay, with a province dropdown to swap which region's data
is shown, and saves it as a standalone HTML file.
'''

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

scenarios = ["baseline", "cleanair", "otpca", "otpnzca", "epnzca"]
pollutants = ["NH3", "NOx", "PM25", "SO2", "VOC"]

category_colors = {"DPEC": "#1f77b4", "2017-Base": "#ff7f0e", "2020-Base": "#2ca02c"}
x_cats = ["DPEC", "2017-Base", "2020-Base"]

titles = [f"{scenario}, {pollutant}" for pollutant in pollutants for scenario in scenarios]

fig = make_subplots(rows = 5, cols = 5, subplot_titles = titles)

path_to_data = "DPEC-2017-2020 Emission Comparisons"

sample_df = pd.read_excel("DPEC-2017-2020 Emission Comparisons/2035/baseline_NH3.xlsx")
sample_df = sample_df.set_index("Unnamed: 0")

for cat, color in category_colors.items():
    fig.add_trace(go.Bar(x = [], y = [], name = cat, marker_color = color, showlegend = True))

fig.add_trace(go.Scatter(x = [], y = [], mode = "markers",
                          marker = dict(symbol = "circle", color = "black", size = 12),
                          name = "2030", showlegend = True))

province_list = ['Total'] + [p for p in sample_df.index.dropna().tolist() if p != 'Total']

for idx, province in enumerate(province_list):
    visible = (idx == 0)
    
    if province == "Total":
        for row, pollutant in enumerate(pollutants, 1):
            for col, scenario in enumerate(scenarios, 1):
                file = f"{scenario}_{pollutant}"
                df = pd.read_excel(f"DPEC-2017-2020 Emission Comparisons/2035/{file}.xlsx")
                df = df.set_index("Unnamed: 0")
                data = df.sum()
                
                data_dpec = data.iloc[0]
                data_2017 = data.iloc[1]
                data_2020 = data.iloc[2]
                
                fig.add_trace(go.Bar(x = x_cats, 
                                     y = [data_dpec, data_2017, data_2020], 
                                     marker_color = [category_colors[c] for c in x_cats], 
                                     visible = visible, showlegend = False), row = row, col = col)
                
        for row, pollutant in enumerate(pollutants, 1):
            for col, scenario in enumerate(scenarios, 1):
                file = f"{scenario}_{pollutant}"
                df = pd.read_excel(f"DPEC-2017-2020 Emission Comparisons/2030/{file}.xlsx")
                df = df.set_index("Unnamed: 0")
                data = df.sum()
                
                data_dpec = data.iloc[0]
                data_2017 = data.iloc[1]
                data_2020 = data.iloc[2]
                
                fig.add_trace(go.Scatter(x = ["DPEC", "2017-Base", "2020-Base"], y = [data_dpec , data_2017, data_2020], mode = "markers",
                             marker = dict(symbol = "circle", size = 12, color = "black"), visible = visible, showlegend = False), 
                             row = row, col = col)
    else:
        for row, pollutant in enumerate(pollutants, 1):
            for col, scenario in enumerate(scenarios, 1):
                file = f"{scenario}_{pollutant}"
                df = pd.read_excel(f"DPEC-2017-2020 Emission Comparisons/2035/{file}.xlsx")
                df = df.set_index("Unnamed: 0")
                data = df.loc[province]
                
                data_dpec = data.iloc[0]
                data_2017 = data.iloc[1]
                data_2020 = data.iloc[2]
                
                fig.add_trace(go.Bar(x = x_cats, 
                                     y = [data_dpec, data_2017, data_2020], 
                                     marker_color = [category_colors[c] for c in x_cats], 
                                     visible = visible, showlegend = False), row = row, col = col)
                
        for row, pollutant in enumerate(pollutants, 1):
            for col, scenario in enumerate(scenarios, 1):
                file = f"{scenario}_{pollutant}"
                df = pd.read_excel(f"DPEC-2017-2020 Emission Comparisons/2030/{file}.xlsx")
                df = df.set_index("Unnamed: 0")
                data = df.loc[province]
                
                data_dpec = data.iloc[0]
                data_2017 = data.iloc[1]
                data_2020 = data.iloc[2]
                
                fig.add_trace(go.Scatter(x = ["DPEC", "2017-Base", "2020-Base"], y = [data_dpec , data_2017, data_2020], mode = "markers",
                             marker = dict(symbol = "circle", size = 12, color = "black"), visible = visible, showlegend = False), 
                             row = row, col = col)
                
traces_per_province = 50
buttons = []
print(len(fig.data))
for idx, province in enumerate(province_list):
    visibility = [False] * len(fig.data)
    start = idx * traces_per_province + 4
    for t in range(traces_per_province):
        visibility[start + t] = True
    buttons.append(dict(label = province, method = 'update',
        args = [{'visible': visibility}, {'title': f'{province} Emission Comparison'}]))

fig.update_layout(
    updatemenus = [dict(buttons = buttons, direction = 'down', x = 0.1, y = 1.15)],
    title = f'{province_list[0]} Emission Comparison', bargap = 0.4
)

fig.write_html("DPEC-2017-2020 Emission Comparisons/emission_comparison_interactive.html")
fig.show()
                
                
                
