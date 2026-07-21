'''
Shared constants and helpers used across multiple scripts in this folder:
province name mappings (Chinese -> English), the province geometry
GeoDataFrame (via cnmaps), the China national boundary mask used to
restrict model grid cells to China, and the get_national_total()
summing helper used by the province choropleth scripts.
'''
 
import geopandas as gpd
import shapely
from cnmaps import get_adm_maps
 
# Provinces/regions to always treat as excluded from province-level choropleths
# (not present in the mainland emission/population datasets used here).
EXCLUDED_REGIONS = ["台湾省", "香港特别行政区", "澳门特别行政区"]
 
# Ordered list of English province names, matching the column order used in
# the emission report spreadsheets (index + column offset = the right cell).
PROVINCE_ARR = ["Beijing", "Tianjin", "Hebei", "Shanxi", "Inner Mongolia", "Liaoning", "Jilin", "Heilongjiang", "Shanghai",
                "Jiangsu", "Zhejiang", "Anhui", "Fujian", "Jiangxi", "Shandong", "Henan", "Hubei", "Hunan", "Guangdong",
                "Guangxi", "Hainan", "Chongqing", "Sichuan", "Guizhou", "Yunnan", "Tibet", "Shaanxi", "Gansu", "Qinghai",
                "Ningxia", "Xinjiang"]
 
# Chinese -> English province name mapping matching the EMISSION REPORT
# spreadsheets' spelling convention (used together with PROVINCE_ARR above
# to look up a province's column index).
PROVINCE_MAP_EMISSIONS = {
    "北京市": "Beijing",
    "天津市": "Tianjin",
    "河北省": "Hebei",
    "山西省": "Shanxi",
    "内蒙古自治区": "Inner Mongolia",
    "辽宁省": "Liaoning",
    "吉林省": "Jilin",
    "黑龙江省": "Heilongjiang",
    "上海市": "Shanghai",
    "江苏省": "Jiangsu",
    "浙江省": "Zhejiang",
    "安徽省": "Anhui",
    "福建省": "Fujian",
    "江西省": "Jiangxi",
    "山东省": "Shandong",
    "河南省": "Henan",
    "湖北省": "Hubei",
    "湖南省": "Hunan",
    "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi",
    "海南省": "Hainan",
    "重庆市": "Chongqing",
    "四川省": "Sichuan",
    "贵州省": "Guizhou",
    "云南省": "Yunnan",
    "西藏自治区": "Tibet",
    "陕西省": "Shaanxi",
    "甘肃省": "Gansu",
    "青海省": "Qinghai",
    "宁夏回族自治区": "Ningxia",
    "新疆维吾尔自治区": "Xinjiang"
}
 
# Chinese -> English province name mapping matching the POPULATION
# PROJECTION dataset's spelling convention (Pop_TOTAL.csv's "V1" column).
# This is not interchangeable with PROVINCE_MAP_EMISSIONS above,
# three provinces are romanized differently (Inner Mongolia/NeiMonggol,
# Yunnan/Yunan, Tibet/Xizang). Use whichever matches the data source you're
# actually looking up against.
PROVINCE_MAP_POPULATION = {
    "北京市": "Beijing",
    "天津市": "Tianjin",
    "河北省": "Hebei",
    "山西省": "Shanxi",
    "内蒙古自治区": "NeiMonggol",
    "辽宁省": "Liaoning",
    "吉林省": "Jilin",
    "黑龙江省": "Heilongjiang",
    "上海市": "Shanghai",
    "江苏省": "Jiangsu",
    "浙江省": "Zhejiang",
    "安徽省": "Anhui",
    "福建省": "Fujian",
    "江西省": "Jiangxi",
    "山东省": "Shandong",
    "河南省": "Henan",
    "湖北省": "Hubei",
    "湖南省": "Hunan",
    "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi",
    "海南省": "Hainan",
    "重庆市": "Chongqing",
    "四川省": "Sichuan",
    "贵州省": "Guizhou",
    "云南省": "Yunan",
    "西藏自治区": "Xizang",
    "陕西省": "Shaanxi",
    "甘肃省": "Gansu",
    "青海省": "Qinghai",
    "宁夏回族自治区": "Ningxia",
    "新疆维吾尔自治区": "Xinjiang"
}
 
 
def get_national_total(wb, sheet_name, row_range, col_offset):
    '''
    Sums every province's value out of an openpyxl workbook sheet, for the
    given row range (sector rows) and column offset (where province columns
    start). Used to print/label a national total alongside a province map.
    '''
    sheet = wb[sheet_name]
    total = 0
    for province in PROVINCE_ARR:
        province_index = PROVINCE_ARR.index(province)
        for r in row_range:
            val = sheet.cell(r, province_index + col_offset).value
            if val:
                total += val
    return total
 
 
def get_province_gdf():
    '''
    Builds a GeoDataFrame of Chinese province geometries via cnmaps,
    suitable for a choropleth: gdf['color'] = gdf['province'].apply(...);
    gdf.plot(color=gdf['color'], ...).
    '''
    records = []
    for province in get_adm_maps(level='省'):
        records.append({
            'province': province['province'],
            'geometry': province['geometry']
        })
    return gpd.GeoDataFrame(records, crs='EPSG:4326')
 
 
def get_china_geometry():
    '''Returns the China national boundary polygon (Natural Earth 110m).'''
    world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
    return world[world['NAME'] == 'China'].geometry.iloc[0]
 
 
def build_in_china_mask(lon, lat):
    '''
    Given 2D lon/lat arrays (matching a model grid's shape), returns a
    boolean array of the same shape that's True where the grid cell's
    center falls within China's national boundary. If you're calling
    this in a loop (e.g. once per file), fetch china_geom = get_china_geometry()
    once beforehand and pass it in, to avoid re-fetching the boundary
    data on every call.
    '''
    if china_geom is None:
        china_geom = get_china_geometry()
    lon_flat = lon.flatten()
    lat_flat = lat.flatten()
    in_china_flat = shapely.contains_xy(china_geom, lon_flat, lat_flat)
    return in_china_flat.reshape(lon.shape)