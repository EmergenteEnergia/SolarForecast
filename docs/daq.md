## Acquisition of historical and real-time forecasted data from GFS server 
The acquisition of historical and real-time forecasted meteorological data involves a remote connection with THREDDS Data Server (TDS). This connection is based on Siphon Python package interacting with the NetCDF Subset Service (NCSS) in order to retrieve NCEP GFS 0.25 Degree Global Forecast Grids.

As output, a file in h5 format is produced containing the post-processed forecasts.

Before running any of the daq functions, the GFS model characteristics corresponding to time range and domain need to be defined. Forecast runtime and products are predetermined.

The GFS forecast system runs four times a day and produces forecasts up to 16 days in advance. The acquisition retrieves all available forecast runtimes at: 00UTC, 06UTC, 12UTC, and 18UTC. Forecast products are collected for 24 hours at every runtime. As time resolution of the GFS forecast model is 3hours, the retrived products have the same resolution, meaning 8 products per day are retrieved by the tool.


### Historical archive data
Use the function daq_arc.py for accesing the TDSCatalog that offers archive dataset for the GFS global 0.25 degree collection of GRIB files. 

In this project historical data is used for developing a meteorological model for solar irradiance prediction based on neaural network. Therefore, the meteorological parameters listed aboved are already predeterminated for archive acquisition as they are related with solar irraadiance.

Archive acquisition parameters:
- Cloud water [kg/m2] -> entire atmosphere (considered as a single layer)
- Downward Long-Wave Rad. Flux [W/m2] -> surface
- Downward Short-Wave Rad. Flux [W/m2] -> surface
- Planetary Boundary Layer Height [m] -> surface
- Precipitable Water [kg/m2] -> entire atmosphere (considered as a single layer) 
- Precipitation Rate [kg/m2/s] -> surface
- Precipitation Rate 3 hour average [kg/m2/s] -> surface
- Air Temperature [K] -> surface
- Boundary Cloud Cover 3 hour average [%]
- Convective Cloud Cover [%]
- Total Cloud Cover [%] -> entire atmosphere 

To watch function arguments and Help facility, use the command:
```bash
$ python3 ~/../repos/EmergenteEnergia/SolarForecast/src/SolarForecast/daq_arc.py --help
```
The entry arguments for aquiring archive datasets from the GFS weather prediction model are:

    -dt1        : starting datetime in format YYYY-MM-DDTHH. e.g: 2020-07-01T00 
    -dt2        : end datetime in format YYYY-MM-DDTHH. Output-file will include until the previous step of this datetime.(numpy datetime based)
    -loc        : site or domain coordinates. If interest is on a single site, enter the decimal coordinates in a comma-separated list (eg: lat=lat1,lon=lon1). If an area of domain is of interest, enter the cardinal extension in decimal coordinates (eg: north=lat1, south=lat2,east=lon1, west=lon2)
    -dst        : directory path where processed datasets will be located 
    -v          : verbose run. Default: False

**Running example:** retrieve one year archive data from the 2021-01-01 at Medellín (lat = 6.25, lon= -75.50)

```bash
$ python3 ~/repos/EmergenteEnergia/SolarForecast/src/SolarForecast/daq_arc.py -dt1 2021-01-01 -dt2 2022-01-01 -loc lat=6.25,lon=-75.50 -dst ~/../archiveData/
```

### Real-time data
Use the function daq.py for accessing the TDSCatalog that offers the latest datasets for the GFS global 0.25-degree collection of GRIB files.

For the acquisition of real-time data, it is possible to select certain parameters of interest from the variables given by the GFS model. The complete list with GFS model variables and levels can be checked [here].(https://www.nco.ncep.noaa.gov/pmb/products/gfs/gfs.t00z.pgrb2.0p25.f003.shtml).

To watch function arguments and Help facility, use the command:
```bash
$ python3 ~/../repos/EmergenteEnergia/SolarForecast/src/SolarForecast/daq.py --help
```
The entry arguments for acquiring archive datasets from the GFS weather prediction model are:

    -dt1        : starting datetime in format YYYY-MM-DDTHH. e.g: 2020-07-01T00 
    -dt2        : end datetime in format YYYY-MM-DDTHH. Output-file will include until the previous step of this datetime.(numpy datetime based)
    -loc        : site or domain coordinates. If a single site is of interest, enter the decimal coordinates in a comma separated list (eg: lat=lat1,lon=lon1). If an area of domain is of interest, enter the cardinal extension in decimal coordinates (eg: north=lat1, south=lat2,east=lon1, west=lon2)
    -prms       : parameters to be processed in a comma-separated list. Use "all" for all available parameters. Use "solar" for default parameters used in the solar irradiance forecast model.
    -dst        : directory path where processed datasets will be located 
    -v          : verbose run. Default: False

**Running example:** retrieve one year of data from the 2021-01-01 for Surface Temperature, Downward Short-Wave irrade, and Planetary Boundary level in the Colombian region

```bash
$ python3 ~/repos/EmergenteEnergia/SolarForecast/src/SolarForecast/daq_arc.py -dt1 2021-01-01 -dt2 2022-01-01 -loc north=15,south=-5,east=-65,west=-80 -prms Temperature_surface,Downward_Short-Wave_Radiation_Flux_surface_Mixed_intervals_Average,Planetary_Boundary_Layer_Height_surface -dst ~/../archiveData/
```
