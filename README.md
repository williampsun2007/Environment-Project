# Environment-Project

Code developed over a summer research project with the **Center for Policy Research on Energy and the Environment (C-PREE)** at Princeton University. The repo has two parts that work together:

1. **Playwright automation** for CNCAP, a web platform used to run province/sector/pollutant emission-reduction scenarios through an air quality model.
2. **Python scripts for formatting, exploring, and visualizing** the emissions and PM2.5 data that go into and come out of that model (referred to here as the Qingfeng, or "Breeze," model).

The automation scripts build "control plan" spreadsheets describing an emissions-reduction scenario, upload them to CNCAP, and download the resulting PM2.5 concentration output. The analysis scripts then turn those raw emissions and PM2.5 files into comparisons, summary tables, and maps/charts.

## Background

**CNCAP** is a web platform where a user uploads a "control plan" (管控方案) spreadsheet — percent emission reductions broken out by province, sector, and pollutant — and runs it through an air quality simulation. The simulation returns PM2.5 concentration predictions as NetCDF (`.nc`) files with a `pred_PM25` variable, plus emission report spreadsheets.

**Qingfeng (Breeze)** is the underlying model CNCAP exposes through its "Online Simulation" interface. This repo doesn't reimplement the model itself — it automates feeding scenarios into it and processes what comes back out.

## Repo Content

### 1. Web automation (Playwright)
Page-object classes (login, home/menu navigation, and the online simulation page) plus a batch runner that logs into CNCAP, uploads a folder of Excel scenario files, and downloads each task's results as a `.zip`, sleeping between batches to give the server time to process.

### 2. Control-plan / scenario generation
Scripts that build the "管控方案" input spreadsheets CNCAP expects, covering a range of experiment designs:
- Flat percent reductions per pollutant (10-100%, in 10% steps)
- Reductions derived from a modeled scenario (e.g. reshaping a 2020→2035 % change table into the control-plan format)
- Combinatorial designs — every 3-sector combination, every pollutant subset (encoded as a binary code), an extra 10% cut applied to one province/pollutant at a time

### 3. Emission data processing
Scripts that compare raw emission report spreadsheets across years (2017/2020 vs. 2030/2035) and scenarios: percent reduction by sector/province, per-capita emissions (merged with population projections), department/sector share of total emissions, and summary tables of total reduction vs. total increase per pollutant, including a check that flags provinces/sectors where PM and BC/OC trends disagree in sign.

### 4. PM2.5 output analysis
Scripts that read the NetCDF output from CNCAP and compute population-weighted exposure metrics: % of China's population exposed above 25 or 35 µg/m³, population-weighted mean PM2.5 by scenario, exposure sensitivity curves as a single pollutant is reduced 10-100%, and difference-from-baseline comparisons across scenarios and meteorological years.

### 5. Population data & projections
Scripts that regrid population rasters (1km and 100m resolution) onto the model's grid, and a set of scripts that build interactive Plotly charts comparing population projections across three data sources (1km grid, 100m grid, and province-level SSP fertility/migration scenarios) against actual census figures, with a per-province dropdown.

### 6. Visualization & mapping
The bulk of the repo: choropleth maps of Chinese provinces (emissions, PM2.5 change, population change) using `cnmaps`/`geopandas`/`cartopy`; stacked bar charts of sector emissions over time; population-weighted PM2.5 exposure curves; and several interactive Plotly HTML dashboards for exploring emissions and population data by province and scenario.

## Scenario & naming conventions

Scenarios referenced throughout the code:

| Abbreviation | Meaning |
|---|---|
| Baseline | No additional emission controls |
| Clean Air | "Clean air" policy scenario |
| OTPCA | On-time-peak, clean air |
| OTPNZCA | On-time-peak, net-zero, clean air |
| EPNZCA | Early-peak, net-zero, clean air |

Pollutants covered: SO2, NOx, VOC, NH3, PM2.5, PM10, BC, OC, and CO2 (in the sector-breakdown scripts). Population scenarios use SSP1-SSP5 (1km/100m gridded data) and a fertility × migration grid (`SSPFer1-5` × `SSPMigr1-3`) for province-level projections. File names generally encode scenario, pollutant, and meteorological/weather year — check the comment at the top of each script for the exact pattern it expects.

### Environment variables
The Playwright automation reads credentials and paths from a `.env` file in the project root:

```
APP_BASE_URL=http://cncap.org.cn/?page_id=944
APP_USERNAME=<your CNCAP username>
APP_PASSWORD=<your CNCAP password>
APP_FILE_PATH=<folder of batch subfolders containing Excel files to upload>
APP_DOWNLOAD_PATH=<folder to save downloaded result .zip files>
```

Note: after installing dependencies, run `playwright install chromium` once — Playwright needs to download its browser binary separately.

## Usage

Run the batch uploader directly:

```bash
python browser_automation/run_batch_automation.py
```

It will process every subfolder under `APP_FILE_PATH` as a batch, uploading each `.xlsx` file as a task and downloading results once done, waiting an hour between batches.

The analysis and visualization scripts are standalone — each one reads specific input files (see the comment at the top and the `pd.read_excel` / `xr.open_dataset` / `np.load` calls near the top of the script) and writes its output (an `.xlsx`, `.png`, or `.html` file) to a specified path. Run them individually with `python <script>.py` once the expected input files are in place.