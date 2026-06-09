import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

df = pd.read_excel("Emission Files/Grid_Data.xlsx", sheet_name = "Sheet")

fig, axes = plt.subplots(nrows = 8, ncols = 5, figsize = (14, 20))

department_colors = {"Power": "blue", "Industry": "orange", "Transportation": "green", "Residential": "red", "Agriculture": "purple"}

for i, pollutant in enumerate(["SO2", "NOx", "VOC", "NH3", "PM25", "PM10", "BC", "OC"]):
    for j, scenario in enumerate(["Baseline", "CleanAir", "OTPCA", "OTPNZCA", "EPNZCA"]):
        ax = axes[i][j]
        
        subset = df[(df["Pollutant"] == pollutant) & (df["Scenario"] == scenario)]
        pivot = subset.pivot(index = "Year", columns = "Department", values ="Total")
        total_pollutant = subset.groupby("Year")['Total'].sum().sort_index()
        
        x = np.arange(len(pivot))
        bottom = np.zeros(len(pivot))
        for department in pivot.columns:
            ax.bar(x, pivot[department].values / total_pollutant, bottom = bottom, color = department_colors[department])
            bottom += pivot[department].values / total_pollutant
            
        ax.set_xticks(x)
        ax.set_xticklabels([str(year) if i % 2 == 0 else "" for i, year in enumerate(pivot.index)], rotation = 45)
        
for j, scenario in enumerate(["Baseline", "CleanAir", "OTPCA", "OTPNZCA", "EPNZCA"]):
    axes[0][j].set_title(scenario)
for i, pollutant in enumerate(["SO2", "NOx", "VOC", "NH3", "PM2.5", "PM10", "BC", "OC"]):
    axes[i][0].set_ylabel(f"{pollutant} Percentage (%)")
for i in range(5):
    axes[7][i].set_xlabel("Year")
    
handles = [mpatches.Patch(color=color, label=dept) for dept, color in department_colors.items()]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=len(department_colors))

plt.tight_layout()
plt.savefig("Emission Files/Stacked_Bar_Chart_Percentage.png", bbox_inches="tight")
plt.show()