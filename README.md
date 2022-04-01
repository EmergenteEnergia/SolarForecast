# Solar Radiation Forecast 
This repository has been created for the acquisition and post-processing of atmospheric variables coming from the **Global Forecast System (GFS)** prediction model, in order to develop an intraday solar radiation forecast for the Colombian region and their in-situ verification.

This documentation describes the general use of the library and details the handling of files and the analysis outcomes corresponding to the meteorological data of a period of one (5) years, obtained for the city of **Medellín- Colombia**, as benchmarking.

Likewise, the methodology using neural networks is outlined and included in the library, where these atmospheric variables are used for building and training a neural network model for the forecast of intraday solar irradiance. The meteorological model will be developed and operated using the Microsoft Azure resources and its results will be validated with local irradiance measurements.

This project attempts to help the optimization of photovoltaic solar energy production at different strategic points in Colombia and eventually, it is desired that the library includes the conversion of the solar resource to solar energy potential useful for site resource assessment and apply techniques for the optimization of solar energy integration into the electricity grid.

## Library and main functionalities
1. [Library Installation](docs/installation.md)
2. [Data Acquisition](docs/daq.md) and [post-processing](docs/posproc.md)
3. [Analysis of meteorological variables](docs/ansys.ipynb)
4. [Neuronal Network for solar irradiance forecast](docs/ann.md)
5. [In situ verification](docs/verif.md)


## Data Archive
1. [Raw Data from the GFS prediction model](data/data_arc.md#1. Raw Data from the GFS prediction model)
2. [Post-processed atmospheric data](data/data_arc.md#2. Post-processed atmospheric data)
3. [Solar irradiance forecast](data/data_arc.md#3. Solar irradiance forecast)


