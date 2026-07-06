import pandas as pd

with pd.ExcelWriter("Emission Files/2017_2020_Emission_Comparison.xlsx", mode = 'a', if_sheet_exists = 'replace') as writer:
    for pollutant in ["SO2", "NOx", "VOC", "NH3", "PM25", "PM10", "BC", "OC"]:
        df_2017 = pd.read_excel("Emission Files/2017_emission_report.xlsx", pollutant)
        df_2020 = pd.read_excel("Emission Files/2020_emission_report.xlsx", pollutant)
    
        df_2017 = df_2017.set_index("sector")
        df_2020 = df_2020.set_index("sector")
    
        df_percent_reduction = pd.DataFrame(index = ["电力", "工业", "民用", "交通", "农业"])
        for region in df_2017.columns:
            df_percent_reduction[region] = round(((df_2017[region] - df_2020[region]) / df_2017[region]) * 100, 2)
    
        df_percent_reduction = df_percent_reduction.fillna(0)
    
        df_percent_reduction.to_excel(writer, pollutant)
    
    
    
            
            