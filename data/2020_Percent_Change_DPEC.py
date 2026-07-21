'''
For each pollutant, renders a 6-panel choropleth of Chinese provinces
showing % emission change vs. 2020 (2030/2035 under two scenarios,
each vs. 2017 and vs. 2020 baselines), with national totals labeled,
and saves each figure as a PNG.
'''

import cartopy.crs as ccrs
import openpyxl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from common import PROVINCE_MAP_EMISSIONS, PROVINCE_ARR, EXCLUDED_REGIONS, get_national_total, get_province_gdf

wb_epnzca_2020 = openpyxl.load_workbook("early_peak-net_zero-clean_air/2020_Emission.xlsx")
wb_epnzca_2030 = openpyxl.load_workbook("early_peak-net_zero-clean_air/2030_Emission.xlsx")
wb_epnzca_2035 = openpyxl.load_workbook("early_peak-net_zero-clean_air/2035_Emission.xlsx")

wb_2017_2030 = openpyxl.load_workbook("Emission Reports/2030/emission_report-epnzca-2017 to 2030.xlsx")
wb_2017_2035 = openpyxl.load_workbook("Emission Reports/2035/emission_report-epnzca-2017 to 2035.xlsx")

wb_2020_2030 = openpyxl.load_workbook("Emission Reports/2030/emission_report-epnzca-2020 to 2030.xlsx")
wb_2020_2035 = openpyxl.load_workbook("Emission Reports/2035/emission_report-epnzca-2020 to 2035.xlsx")

gdf = get_province_gdf()

pollutant_ticks = {
    "SO2": [-90, -60, -30, 0, 30, 60, 90],
    "NOx": [-70, -50, -20, 0, 20, 50, 70],
    "VOC": [-90, -60, -30, 0, 30, 60, 90],
    "NH3": [-50, -30, -10, 0, 10, 30, 50],
    "PM25": [-90, -60, -30, 0, 30, 60, 90]
}

pollutant_labels = {
    "SO2": ['-90%', '-60%', '-30%', '0%', '30%', '60%', '90%'],
    "NOx": ['-70%', '-50%', '-20%', '0%', '20%', '50%', '70%'],
    "VOC": ['-90%', '-60%', '-30%', '0%', '30%', '60%', '90%'],
    "NH3": ['-50%', '-30%', '-10%', '0%', '10%', '30%', '50%'],
    "PM25": ['-90%', '-60%', '-30%', '0%', '30%', '60%', '90%']
}

for pollutant in ["SO2", "NOx", "VOC", "NH3", "PM25"]:
    cmap = plt.get_cmap('RdYlGn')
    vmax = pollutant_ticks[pollutant][-1]
    vmin = pollutant_ticks[pollutant][0]
    norm = Normalize(vmin = vmin, vmax = vmax) 
    poll_max = -1000
    poll_min = 1000 
    
    def get_color_2017_2030(name):
        global poll_max, poll_min
        sheet = wb_2017_2030[pollutant]
        sheet_2020 = wb_epnzca_2020[pollutant]
        if name in PROVINCE_MAP_EMISSIONS and name not in EXCLUDED_REGIONS:
            english_name = PROVINCE_MAP_EMISSIONS[name]
            province_index = PROVINCE_ARR.index(english_name)
            total_2030 = 0
            for r in range(9, 14):
                total_2030 += sheet.cell(r, province_index + 5).value
                
            total_2020 = 0
            for r in range(3, 8):
                total_2020 += sheet_2020.cell(r, province_index + 3).value
            poll_max = max(poll_max, (total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            poll_min = min(poll_min, (total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            return cmap(norm((total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0))
        return "lightgrey"
    
    def get_color_2017_2035(name):
        global poll_max, poll_min
        sheet = wb_2017_2035[pollutant]
        sheet_2020 = wb_epnzca_2020[pollutant]
        if name in PROVINCE_MAP_EMISSIONS and name not in EXCLUDED_REGIONS:
            english_name = PROVINCE_MAP_EMISSIONS[name]
            province_index = PROVINCE_ARR.index(english_name)
            total_2035 = 0
            for r in range(9, 14):
                total_2035 += sheet.cell(r, province_index + 5).value

            total_2020 = 0
            for r in range(3, 8):
                total_2020 += sheet_2020.cell(r, province_index + 3).value
            poll_max = max(poll_max, (total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            poll_min = min(poll_min, (total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            return cmap(norm((total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0))
        return "lightgrey"

    def get_color_2020_2030(name):
        global poll_max, poll_min
        sheet = wb_2020_2030[pollutant]
        sheet_2020 = wb_epnzca_2020[pollutant]
        if name in PROVINCE_MAP_EMISSIONS and name not in EXCLUDED_REGIONS:
            english_name = PROVINCE_MAP_EMISSIONS[name]
            province_index = PROVINCE_ARR.index(english_name)
            total_2030 = 0
            for r in range(9, 14):
                total_2030 += sheet.cell(r, province_index + 5).value
            
            total_2020 = 0
            for r in range(3, 8):
                total_2020 += sheet_2020.cell(r, province_index + 3).value
            poll_max = max(poll_max, (total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            poll_min = min(poll_min, (total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            return cmap(norm((total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0))
        return "lightgrey"
    
    def get_color_2020_2035(name):
        global poll_max, poll_min
        sheet = wb_2020_2035[pollutant]
        sheet_2020 = wb_epnzca_2020[pollutant]
        if name in PROVINCE_MAP_EMISSIONS and name not in EXCLUDED_REGIONS:
            english_name = PROVINCE_MAP_EMISSIONS[name]
            province_index = PROVINCE_ARR.index(english_name)
            total_2035 = 0
            for r in range(9, 14):
                total_2035 += sheet.cell(r, province_index + 5).value
            
            total_2020 = 0
            for r in range(3, 8):
                total_2020 += sheet_2020.cell(r, province_index + 3).value
            poll_max = max(poll_max, (total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            poll_min = min(poll_min, (total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            return cmap(norm((total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0))
        return "lightgrey"
    
    def get_color_2030(name):
        global poll_max, poll_min
        sheet = wb_epnzca_2030[pollutant]
        sheet_2020 = wb_epnzca_2020[pollutant]
        if name in PROVINCE_MAP_EMISSIONS and name not in EXCLUDED_REGIONS:
            english_name = PROVINCE_MAP_EMISSIONS[name]
            province_index = PROVINCE_ARR.index(english_name)
            total_2030 = 0
            for r in range(3, 8):
                total_2030 += sheet.cell(r, province_index + 3).value
                
            total_2020 = 0
            for r in range(3, 8):
                total_2020 += sheet_2020.cell(r, province_index + 3).value
            poll_max = max(poll_max, (total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            poll_min = min(poll_min, (total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            return cmap(norm((total_2030 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0))
        return "lightgrey"

    def get_color_2035(name):
        global poll_max, poll_min
        sheet = wb_epnzca_2035[pollutant]
        sheet_2020 = wb_epnzca_2020[pollutant]
        if name in PROVINCE_MAP_EMISSIONS and name not in EXCLUDED_REGIONS:
            english_name = PROVINCE_MAP_EMISSIONS[name]
            province_index = PROVINCE_ARR.index(english_name)
            total_2035 = 0
            for r in range(3, 8):
                total_2035 += sheet.cell(r, province_index + 3).value
                
            total_2020 = 0
            for r in range(3, 8):
                total_2020 += sheet_2020.cell(r, province_index + 3).value
            poll_max = max(poll_max, (total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            poll_min = min(poll_min, (total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0)
            return cmap(norm((total_2035 - total_2020) / total_2020 * 100 if total_2020 != 0 else 0))
        return "lightgrey"
    
    fig, ax = plt.subplots(nrows = 3, ncols = 2, figsize = (30, 25), subplot_kw = {'projection': ccrs.PlateCarree()})
    
    gdf['color'] = gdf['province'].apply(get_color_2030)
    gdf.plot(color = gdf['color'], ax = ax[0][0], edgecolor = 'black', linewidth = 0.1)
    ax[0][0].set_title(f"2030 Emissions from DPEC (% change vs 2020)")
    total = get_national_total(wb_epnzca_2030, pollutant, range(3, 8), 3)
    ax[0][0].text(0.5, 0.05, f"National Total: {total:,.0f} tons", 
                  transform = ax[0][0].transAxes, ha = 'center', fontsize = 10)
    
    gdf['color'] = gdf['province'].apply(get_color_2035)
    gdf.plot(color = gdf['color'], ax = ax[0][1], edgecolor = 'black', linewidth = 0.1)
    ax[0][1].set_title(f"2035 Emissions from DPEC (% change vs 2020)")
    total = get_national_total(wb_epnzca_2035, pollutant, range(3, 8), 3)
    ax[0][1].text(0.5, 0.05, f"National Total: {total:,.0f} tons", 
                  transform = ax[0][1].transAxes, ha = 'center', fontsize = 10)
    
    gdf['color'] = gdf['province'].apply(get_color_2017_2030)
    gdf.plot(color = gdf['color'], ax = ax[1][0], edgecolor = 'black', linewidth = 0.1)
    ax[1][0].set_title(f"2030 Emissions Relative to 2017 (% change vs 2020)")
    total = get_national_total(wb_2017_2030, pollutant, range(9, 14), 5)
    ax[1][0].text(0.5, 0.05, f"National Total: {total:,.0f} tons", 
                  transform = ax[1][0].transAxes, ha = 'center', fontsize = 10)
    
    gdf['color'] = gdf['province'].apply(get_color_2017_2035)
    gdf.plot(color = gdf['color'], ax = ax[1][1], edgecolor = 'black', linewidth = 0.1)
    ax[1][1].set_title(f"2035 Emissions Relative to 2017 (% change vs 2020)")
    total = get_national_total(wb_2017_2035, pollutant, range(9, 14), 5)
    ax[1][1].text(0.5, 0.05, f"National Total: {total:,.0f} tons", 
                  transform = ax[1][1].transAxes, ha = 'center', fontsize = 10)
    
    gdf['color'] = gdf['province'].apply(get_color_2020_2030)
    gdf.plot(color = gdf['color'], ax = ax[2][0], edgecolor = 'black', linewidth = 0.1)
    ax[2][0].set_title(f"2030 Emissions Relative to 2020 (% change vs 2020)")
    total = get_national_total(wb_2020_2030, pollutant, range(9, 14), 5)
    ax[2][0].text(0.5, 0.05, f"National Total: {total:,.0f} tons", 
                  transform = ax[2][0].transAxes, ha = 'center', fontsize = 10)
    
    gdf['color'] = gdf['province'].apply(get_color_2020_2035)
    gdf.plot(color = gdf['color'], ax = ax[2][1], edgecolor = 'black', linewidth = 0.1)
    ax[2][1].set_title(f"2035 Emissions Relative to 2020 (% change vs 2020)")
    total = get_national_total(wb_2020_2035, pollutant, range(9, 14), 5)
    ax[2][1].text(0.5, 0.05, f"National Total: {total:,.0f} tons", 
                  transform = ax[2][1].transAxes, ha = 'center', fontsize = 10)
            
    plt.subplots_adjust(hspace = 0.1, wspace = 0.05)
    
    sm = cm.ScalarMappable(cmap = cmap, norm = norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax = ax, orientation = 'vertical', pad = 0.02)
    cbar.set_label('Percent Change from 2020 Emissions (%)', fontsize = 14)
    cbar.set_ticks(pollutant_ticks[pollutant])
    cbar.set_ticklabels(pollutant_labels[pollutant])
    
    print(f"Pollutant: {pollutant}, Max: {poll_max}, Min: {poll_min}")

    fig.suptitle(f'Emission Percent Change from 2020 for {pollutant} (EPNZCA Scenario)', fontsize = 18, fontweight = 'bold')
    plt.savefig(f"Emission Files/Percent Change from 2020 Baseline/EPNZCA/{pollutant}_Map.png")
    plt.close(fig)
    
print("Finished!")