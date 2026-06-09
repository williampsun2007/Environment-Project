import pandas as pd
from pathlib import Path

df = pd.read_csv(r"C:\Users\sunyi\Environment_Project\Population_Projection\Population_Projection_Data\Province\Pop_TOTAL.csv")
df.dropna(inplace = True)

df = df[df["V2"] == "_SSPFer2_SSPMigr3"]

columns_to_drop = []
for col in df.columns:
    if col != "V1" and col != "2020" and col != "2035":
        columns_to_drop.append(col)
        
df.drop(columns_to_drop, axis = 1, inplace = True)

df.reset_index(inplace = True)
df.drop("index", axis = 1, inplace = True)

df.replace("NeiMonggol", "Inner Mongolia", inplace = True)
df.replace("Yunan", "Yunnan", inplace = True)
df.replace("Xizang", "Tibet", inplace = True)

for scenario in ["Baseline", "CleanAir", "OTPCA", "OTPNZCA", "EPNZCA"]:
    if scenario == "Baseline":
        scenario_full_name = "baseline"
    elif scenario == "CleanAir":
        scenario_full_name = "clean_air"
    elif scenario == "EPNZCA":
        scenario_full_name = "early_peak-net_zero-clean_air"
    elif scenario == "OTPCA":
        scenario_full_name = "on-time_peak-clean_air"
    elif scenario == "OTPNZCA":
        scenario_full_name = "on-time_peak-net_zero-clean_air"
    
    df_scenario_2020 = pd.read_excel(rf"C:\Users\sunyi\Environment_Project\{scenario}_All_Years\{scenario_full_name}_2020_Emission.xlsx", sheet_name = "PM25")
    df_scenario_2035 = pd.read_excel(rf"C:\Users\sunyi\Environment_Project\{scenario}_All_Years\{scenario_full_name}_2035_Emission.xlsx", sheet_name = "PM25")

    df_part_1 = df_scenario_2020.iloc[0]
    df_part_2 = df_scenario_2035.iloc[0]
    
    df_part_1.drop(["category", "month"], inplace = True)
    df_part_1 = pd.DataFrame(df_part_1)
    df_part_1 = df_part_1.reset_index()
    df_part_1.columns = ["V1", "Total Emission"]
    
    df_part_2.drop(["category", "month"], inplace = True)
    df_part_2 = pd.DataFrame(df_part_2)
    df_part_2 = df_part_2.reset_index()
    df_part_2.columns = ["V1", "Total Emission"]
    
    df_merged = pd.merge(df, df_part_1, on = "V1", how = "left")
    df_merged = pd.merge(df_merged, df_part_2, on = "V1", how = "left")
    
    df_merged.columns = ["Province", "2020 Pop.", "2035 Pop.", "2020 Emission", "2035 Emission"]
    df_merged["2020 Per Capita"] = df_merged["2020 Emission"] / df_merged["2020 Pop."]
    df_merged["2035 Per Capita"] = df_merged["2035 Emission"] / df_merged["2035 Pop."]
    
    df_merged.to_excel(rf"C:\Users\sunyi\Environment_Project\40 Scenarios Per Capita\{scenario_full_name}_Per_Capita.xlsx", index = False)

print("Finished!")
        
