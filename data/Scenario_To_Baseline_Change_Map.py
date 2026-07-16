import xarray as xr
import geopandas as gpd
import netCDF4 as nc
from shapely.vectorized import contains
import numpy as np
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs

ds = nc.Dataset("2017_Base_Data/PM25.nc")
world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")
china = world[world['NAME'] == 'China']

lon_flat = ds["lon"][:].flatten()
lat_flat = ds["lat"][:].flatten()

in_china_flat = contains(china.geometry.iloc[0], lon_flat, lat_flat)

in_china = in_china_flat.reshape(ds["lon"].shape)

provinces = cfeature.NaturalEarthFeature(
    category = 'cultural',
    name = 'admin_1_states_provinces_lines',
    scale = '50m',
    facecolor = 'none'
)

for met_year in range(2017, 2025):
    baseline = xr.open_dataset(f"NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_baseline_{met_year}Met.nc")
    cleanair = xr.open_dataset(f"NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_clean-air_{met_year}Met.nc")
    otpca = xr.open_dataset(f"NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_on-time-peak-clean-air_{met_year}Met.nc")
    otpnzca = xr.open_dataset(f"NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_on-time-peak-net-zero-clean-air_{met_year}Met.nc")
    epnzca = xr.open_dataset(f"NC Files and Emission Reports - 2020 to 2035/EmissionReductions2035_early-peak-net-zero-clean-air_{met_year}Met.nc")
    
    data_baseline = baseline["pred_PM25"].mean(dim = "time").values
    data_cleanair = cleanair["pred_PM25"].mean(dim = "time").values
    data_otpca = otpca["pred_PM25"].mean(dim = "time").values
    data_otpnzca = otpnzca["pred_PM25"].mean(dim = "time").values
    data_epnzca = epnzca["pred_PM25"].mean(dim = "time").values
    
    data_baseline[~in_china] = np.nan
    data_cleanair[~in_china] = np.nan
    data_otpca[~in_china] = np.nan
    data_otpnzca[~in_china] = np.nan
    data_epnzca[~in_china] = np.nan
    
    fig, ax = plt.subplots(nrows = 2, ncols = 2, figsize = (18, 10), subplot_kw = {'projection': ccrs.PlateCarree()})
    cmap = plt.cm.RdBu_r
    
    data_difference_cleanair = data_cleanair - data_baseline
    data_difference_otpca = data_otpca - data_baseline
    data_difference_otpnzca = data_otpnzca - data_baseline
    data_difference_epnzca = data_epnzca - data_baseline
    
    ax[0][0].pcolormesh(ds["lon"], ds["lat"], data_difference_cleanair, cmap = cmap, vmin = -35, vmax = 35)
    ax[0][1].pcolormesh(ds["lon"], ds["lat"], data_difference_otpca, cmap = cmap, vmin = -35, vmax = 35)
    ax[1][0].pcolormesh(ds["lon"], ds["lat"], data_difference_otpnzca, cmap = cmap, vmin = -35, vmax = 35)
    im = ax[1][1].pcolormesh(ds["lon"], ds["lat"], data_difference_epnzca, cmap = cmap, vmin = -35, vmax = 35)
    
    ax[0][0].set_title("Cleanair")
    ax[0][1].set_title("OTPCA")
    ax[1][0].set_title("OTPNZCA")
    ax[1][1].set_title("EPNZCA")
    
    for r in range(0, 2):
        for c in range(0, 2):
            ax[r][c].coastlines()
            ax[r][c].add_feature(cfeature.BORDERS)
            ax[r][c].add_feature(provinces, edgecolor = 'black', linewidth = 0.5)

    fig.suptitle(f"Difference in PM2.5 Concentration from Baseline to Other Scenarios throughout China, {met_year} Met Year")
    plt.colorbar(im, ax = ax.ravel().tolist(), label = "PM2.5 Change (Scenario - Baseline) [µg/m³]", shrink = 0.6)
    plt.savefig(f"Emission Files/Difference from Baseline Maps/PM25_Difference_From_Baseline_2020-2035_{met_year}Met.png")
    plt.show()
    