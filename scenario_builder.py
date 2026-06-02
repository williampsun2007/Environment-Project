from scipy.stats.qmc import Sobol
import pandas as pd
from itertools import product
import openpyxl

provinces = ["北京市", "天津市", "河北省", "山西省", "内蒙古自治区", "辽宁省", "吉林省", 
             "黑龙江省", "上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", 
             "山东省", "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区", "海南省", 
             "重庆市", "四川省", "贵州省", "云南省", "西藏自治区", "陕西省", "甘肃省", 
             "青海省", "宁夏回族自治区", "新疆维吾尔自治区"]

departments = ["电力", "工业", "民用", "交通", "农业"]

pollutants = ["SO2", "NOX", "VOC", "NH3", "PM"]

reduction_ranges = {
    "SO2": (0, 40),
    "NOX": (0, 20),
    "VOC": (0, 50),
    "NH3": (0, 35),
    "PM":  (0, 60)
}

num_scenarios = 128
sampler = Sobol(d=5, scramble=True)
samples = sampler.random(n=num_scenarios)

for scenario_idx, sample in enumerate(samples):
    rows = []
    reductions = {}
    
    for i, pollutant in enumerate(pollutants):
        low, high = reduction_ranges[pollutant]
        reductions[pollutant] = round(low + sample[i] * (high - low), 2)

    wb = openpyxl.load_workbook(r"C:\Users\sunyi\Environment_Project\管控方案模板.xlsx")
    ws = wb['管控方案']
    ws.delete_rows(3, 10000)

    for province, department, pollutant in product(provinces, departments, pollutants):
        rows.append({
            "Province": province,
            "Department": department,
            "Pollutant": pollutant,
            "Reduction (%)": reductions[pollutant]
        })

    for row in rows:
        ws.append([row.get("Province"), row.get("Department"), row.get("Pollutant"), row.get("Reduction (%)")])

    wb.save(rf"C:\Users\sunyi\Environment_Project\May-21-2026_Excel_Files\May-21-2026-{scenario_idx:03d}_2017_2017.xlsx")

print("All scenarios generated!")