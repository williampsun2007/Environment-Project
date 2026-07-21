'''
Builds an interactive Plotly chart comparing population projection
ranges/means across three datasets (1km, 100m, province-resolution)
per province, with min/max shaded bands and a province dropdown, and
saves it as a standalone HTML file.
'''

import pandas as pd
import plotly.graph_objects as go

df_1km = pd.read_excel("Population Graph Data/1km_Resolution_Data.xlsx")
df_100m = pd.read_excel("Population Graph Data/100m_Resolution_Data.xlsx")
df_prov = pd.read_excel("Population Graph Data/Province_Resolution_data.xlsx")

data_cols_1km = [c for c in df_1km.columns if '_' in str(c)]
years_1km = sorted(set(int(c.split('_')[1]) for c in data_cols_1km))

year_cols_100m = [c for c in df_100m.columns if '_' in str(c)]
years_100m_all = sorted(set(int(c.split('_')[1]) for c in year_cols_100m))
years_100m = [2015] + years_100m_all

years_prov = list(range(2010, 2101))

province_list = ['Total'] + [p for p in df_1km['Province'].dropna().tolist() if p != 'Total']

fig = go.Figure()

for idx, province in enumerate(province_list):
    visible = (idx == 0)
    
    if province == 'Total':
        km_min, km_max, km_mean = [], [], []
        for year in years_1km:
            cols = [c for c in data_cols_1km if c.endswith(f'_{year}')]
            vals = df_1km[cols].sum().values.astype(float)
            km_min.append(vals.min())
            km_max.append(vals.max())
            km_mean.append(vals.mean())
        fig.add_trace(go.Scatter(x = years_1km + years_1km[::-1], y = km_max + km_min[::-1],
            fill = 'toself', fillcolor = 'rgba(0,200,0,0.2)', line = dict(color = 'rgba(0,0,0,0)'),
            showlegend = False, visible = visible, name = '1km range'))
        fig.add_trace(go.Scatter(x = years_1km, y = km_mean, line = dict(color = 'green', width = 2),
            name = '1km dataset', visible = visible))

        total_row = df_100m[df_100m['Province'] == 'Total'].iloc[0]
        base_2015 = float(total_row['Population (2015)'])
        ssp_min, ssp_max, ssp_mean = [base_2015], [base_2015], [base_2015]
        for year in years_100m_all:
            cols = [c for c in year_cols_100m if c.endswith(f'_{year}')]
            vals = total_row[cols].values.astype(float)
            ssp_min.append(vals.min())
            ssp_max.append(vals.max())
            ssp_mean.append(vals.mean())
        fig.add_trace(go.Scatter(x = years_100m + years_100m[::-1], y = ssp_max + ssp_min[::-1],
            fill = 'toself', fillcolor = 'rgba(200,0,0,0.2)', line = dict(color = 'rgba(0,0,0,0)'),
            showlegend = False, visible = visible, name = '100m range'))
        fig.add_trace(go.Scatter(x = years_100m, y = ssp_mean, line = dict(color = 'red', width = 2, dash = 'dash'),
            name = '100m dataset', visible = visible))

        national_prov = df_prov.groupby('V2')[[str(y) for y in years_prov]].sum()
        prov_min = national_prov.min()
        prov_max = national_prov.max()
        prov_mean = national_prov.mean()
        fig.add_trace(go.Scatter(x = years_prov + years_prov[::-1], y = list(prov_max) + list(prov_min)[::-1],
            fill = 'toself', fillcolor = 'rgba(0,0,200,0.2)', line = dict(color='rgba(0,0,0,0)'),
            showlegend = False, visible = visible, name = 'Province range'))
        fig.add_trace(go.Scatter(x = years_prov, y = list(prov_mean), line = dict(color = 'blue', width = 2),
            name = 'Province dataset', visible = visible))

    else:
        row_1km = df_1km[df_1km['Province'] == province]
        if not row_1km.empty:
            row_1km = row_1km.iloc[0]
            km_min, km_max, km_mean = [], [], []
            for year in years_1km:
                cols = [c for c in data_cols_1km if c.endswith(f'_{year}')]
                vals = row_1km[cols].values.astype(float)
                km_min.append(vals.min())
                km_max.append(vals.max())
                km_mean.append(vals.mean())
            fig.add_trace(go.Scatter(x = years_1km + years_1km[::-1], y = km_max + km_min[::-1],
                fill = 'toself', fillcolor = 'rgba(0,200,0,0.2)', line = dict(color = 'rgba(0,0,0,0)'),
                showlegend = False, visible = visible, name = f'1km range'))
            fig.add_trace(go.Scatter(x = years_1km, y = km_mean, line = dict(color = 'green', width = 2),
                name = '1km dataset', visible = visible))

        row_100m = df_100m[df_100m['Province'] == province]
        if not row_100m.empty:
            row_100m = row_100m.iloc[0]
            base_2015 = float(row_100m['Population (2015)'])
            ssp_min, ssp_max, ssp_mean = [base_2015], [base_2015], [base_2015]
            for year in years_100m_all:
                cols = [c for c in year_cols_100m if c.endswith(f'_{year}')]
                vals = row_100m[cols].values.astype(float)
                ssp_min.append(vals.min())
                ssp_max.append(vals.max())
                ssp_mean.append(vals.mean())
            fig.add_trace(go.Scatter(x = years_100m + years_100m[::-1], y = ssp_max + ssp_min[::-1],
                fill = 'toself', fillcolor = 'rgba(200,0,0,0.2)', line = dict(color = 'rgba(0,0,0,0)'),
                showlegend = False, visible = visible, name = '100m range'))
            fig.add_trace(go.Scatter(x = years_100m, y = ssp_mean, line = dict(color = 'red', width = 2, dash = 'dash'),
                name = '100m dataset', visible = visible))

        rows_prov = df_prov[df_prov['V1'] == province]
        if not rows_prov.empty:
            prov_min = rows_prov[[str(y) for y in years_prov]].min()
            prov_max = rows_prov[[str(y) for y in years_prov]].max()
            prov_mean = rows_prov[[str(y) for y in years_prov]].mean()
            fig.add_trace(go.Scatter(x = years_prov + years_prov[::-1], y = list(prov_max) + list(prov_min)[::-1],
                fill = 'toself', fillcolor ='rgba(0,0,200,0.2)', line = dict(color = 'rgba(0,0,0,0)'),
                showlegend = False, visible = visible, name = 'Province range'))
            fig.add_trace(go.Scatter(x = years_prov, y = list(prov_mean), line = dict(color = 'blue', width = 2),
                name = 'Province dataset', visible = visible))

traces_per_province = 6 
buttons = []
for idx, province in enumerate(province_list):
    visibility = [False] * len(fig.data)
    start = idx * traces_per_province
    for t in range(traces_per_province):
        visibility[start + t] = True
    buttons.append(dict(label = province, method = 'update',
        args = [{'visible': visibility}, {'title': f'{province} Population Projection'}]))

fig.update_layout(
    updatemenus = [dict(buttons = buttons, direction = 'down', x = 0.1, y = 1.15)],
    title = f'{province_list[0]} Population Projection',
    xaxis_title = 'Year',
    yaxis_title = 'Population'
)

fig.write_html("Population Graph Data/province_population_interactive.html")
fig.show()