import openpyxl
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.patches as mpatches

baseline_path = "Baseline_All_Years"
clean_air_path = "CleanAir_All_Years"
otpca_path = "OTPCA_All_Years"
otpnzca_path = "OTPNZCA_All_Years"
epnzca_path = "EPNZCA_All_Years"

fig, axes = plt.subplots(nrows = 5, ncols = 1, figsize = (14, 30))

department_colors = {"Power": "blue", "Industry": "orange", "Transportation": "green", "Residential": "red", "Agriculture": "purple"}

count = 0
for scenario_path in [baseline_path, clean_air_path, otpca_path, otpnzca_path, epnzca_path]:
    files = sorted(Path(scenario_path).glob("*.xlsx"))
    
    data = {"Power": [], "Industry": [], "Transportation": [], "Residential": [], "Agriculture": []}
    for file in files:
        wb = openpyxl.load_workbook(file)
        ws = wb["CO2"]
        
        for r in range(3, 8):
            dep_total = 0
            for c in range(3, 34):
                dep_total += ws.cell(row = r, column = c).value
            
            if (r == 3):
                data["Power"].append(dep_total)
            elif (r == 4):
                data["Industry"].append(dep_total)
            elif (r == 5):
                data["Transportation"].append(dep_total)
            elif (r == 6):
                data["Residential"].append(dep_total)
            elif (r == 7):
                data["Agriculture"].append(dep_total)
                
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        
    for industry in ["Power", "Industry", "Transportation", "Residential", "Agriculture"]:
        axes[count].plot(x, data[industry], department_colors[industry], 
                                linestyle = '--', marker = 'o', markerfacecolor = 'white', markeredgecolor = 'black', markeredgewidth = 1.5)
    axes[count].set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9])
    axes[count].set_xticklabels([2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060], rotation = 45)
    count += 1
        
for index, scenario in enumerate(["Baseline", "Clean Air", "OTPCA", "OTPNZCA", "EPNZCA"]):
    axes[index].set_title(str(scenario))
    axes[index].set_ylabel("CO2 Emissions (tons)")
    
handles = [mpatches.Patch(color=color, label=dept) for dept, color in department_colors.items()]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=len(department_colors))

plt.tight_layout(h_pad = 4)
plt.savefig("Emission Files/CO2_Scenarios.png", bbox_inches="tight")
plt.show()
    
