# Solar Forecast
This repository contains the source code for the intraday forecast process of solar global horizontal irradiance and surface temperature based on numerical weather prediction models and, coupled with neural network and data analysis.

The method uses as primary input the products of the Global Forecasting System (GFS) from NOAA. The forecasted data is post-processed and employed for building and training a neural network model to produce intraday solar irradiance and temperature forecasts. 

The project is supported by Microsoft and GEO and will be developed and operated using the Microsoft Planetary Computer and Microsoft Azure resources.

## Main functionalities

* Acquisition of historical and real-time forecasted data from the GFS server
* Post-processing of data
* Analysis of meteorological variables
* Neural network method
* Intraday irradiance forecast generation

## Install

* Make sure you have installed 
    - python3
    - pip 
    - virtualenv

* Create a python virtual environment called "SolarForecast"

```bash
$ mkdir ~/virtualEnvs
$ virtualenv -p python3 ~/virtualEnvs/SolarForecast/
```

* Clone the repository in the repos folder 

```bash
$ mkdir ~/repos/
$ cd ~/repos/
$ git clone git@github.com:EmergenteEnergia/SolarForecast.git
```

* Activate the virtual environment and install the library using pip

```bash
$ source ~/virtualEnvs/SolarForecast/bin/activate
(SolarForecast)$ pip install ~/repos/EmergenteEnergia/SolarForecast/
```

## Tests

To test the library, go to the repos root directory of the repository and run pytest

```bash
$ cd ~/repos/EmergenteEnergia/SolarForecast/
$ pytest # run all tests in fast mode
$ pytest -vv -s # run test in verbose (vv) mode and log to screen output (s) 
```
