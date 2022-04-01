from datetime import datetime, timedelta
import pytz
from siphon.catalog import TDSCatalog
from siphon.ncss import NCSS

import gnal_fncs as fnc

class GFSmodel():

    def __init__(self,dset_ref,res,fc,dt1,dt2,loc,prms,vlev,verbose):
        global log
        log = fnc.simple_log if verbose else fnc.ignore
        model_type = 'Forecast Model Data'
        res_name = 'Quarter' if res=='0p25' else 'Half'

        self.model_type = model_type
        self.dset_ref = dset_ref
        self.res_ref = f'GFS {res_name} Degree Forecast'
        self.vlev = vlev if isinstance(vlev, int) else None
        self.start = dt1.astype(datetime)
        self.end = None if dset_ref == 'latest' or dset_ref == 'archive' else dt2.astype(datetime)
        self.loc = loc
        self.fc = fc if dset_ref == 'archive' else 0
        self.prms = prms
        self.connected = False
        self.missing_flg = False
        log('\n  #### Loading of {} from {} dataset  ####'.format(model_type,dset_ref))
        str_fcprd = '{:02d}H'.format(fc) if dset_ref == 'archive' else dset_ref
        log('    Fcst date: {}UTC  -  Fcst prdct hrzn: {}\n'.format(
            self.start.strftime("%Y%m%d-%H"),str_fcprd))

    def connect_to_archive(self):
        catalog_url = 'https://rda.ucar.edu/thredds/catalog/files/g/ds084.1/catalog.xml'
        access_url_key = 'NetcdfSubset'

        data_catlg = TDSCatalog(catalog_url)
        tds_catlg = TDSCatalog(data_catlg.catalog_refs[self.start.strftime("%Y")].href)
        gfs_url = tds_catlg.catalog_refs[self.start.strftime("%Y%m%d")].href
        gfs = TDSCatalog(gfs_url)

        dset_name='gfs.0p25.{}.f{:03d}.grib2'.format(self.start.strftime("%Y%m%d%H"),self.fc)

        self.dataset = gfs.datasets[dset_name]
        dset_url = self.dataset.access_urls[access_url_key]

        self.ncss = NCSS(dset_url)
        self.query = self.ncss.query()
        self.connected = True
        log('\n  #### Succesful server connection!  ####\n')

    def connect_to_catalog(self):
        catalog_url = 'https://thredds.ucar.edu/thredds/catalog.xml'
        access_url_key = 'NetcdfSubset'

        data_catlg = TDSCatalog(catalog_url)
        tds_catlg = TDSCatalog(data_catlg.catalog_refs[self.model_type].href)
        gfs_url = tds_catlg.catalog_refs[self.res_ref].href
        gfs = TDSCatalog(gfs_url)

        for ref in gfs.datasets.keys():
            if self.dset_ref in ref.lower():
                dset_name = ref

        self.dataset = gfs.datasets[dset_name]
        dset_url = self.dataset.access_urls[access_url_key]

        self.ncss = NCSS(dset_url)
        self.query = self.ncss.query()
        self.connected = True
        log('\n  #### Succesful server connection!  ####\n')

    def set_query_loc(self):
        if len(self.loc) == 2:
            self.lat = self.loc['lat']
            self.lon = self.loc['lon']
            self.query.lonlat_point(self.lon, self.lat)
        elif len(self.loc) == 4:
            self.lat = [self.loc['north'],self.loc['south']]
            self.lon = [self.loc['east'],self.loc['west']]
            self.query.lonlat_box(north=self.loc['north'],
                                  south=self.loc['south'],
                                  east=self.loc['east'],
                                  west=self.loc['west'])

    def set_query_time_range(self):
        if self.end:
            self.query.time_range(pytz.timezone("UTC").localize(self.start),
                                  pytz.timezone("UTC").localize(self.end))
        else:
            self.query.time(self.start) if self.dset_ref != 'archive' else self.query.time(self.start+ timedelta(hours = self.fc))

    def set_query_variables(self):
        if self.prms == 'all':
            self.prms = list(self.ncss.variables)
        elif self.prms == 'solar':
            av = 6 if self.fc % 6 == 0 else 3
            self.prms = ['Temperature_surface',
                         #'Wind_speed_gust_surface',
                         #'u-component_of_wind_isobaric',
                         #'v-component_of_wind_isobaric',
                         #'Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average',
                         'Total_cloud_cover_entire_atmosphere_{}_Hour_Average'.format(av),
                         'Cloud_water_entire_atmosphere_single_layer',
                         #'Low_cloud_cover_low_cloud_Mixed_intervals_Average',
                         #'Medium_cloud_cover_middle_cloud_Mixed_intervals_Average',
                         #'High_cloud_cover_high_cloud_Mixed_intervals_Average',
                         #'Total_cloud_cover_boundary_layer_cloud_Mixed_intervals_Average',
                         'Total_cloud_cover_boundary_layer_cloud_{}_Hour_Average'.format(av),
                         'Total_cloud_cover_convective_cloud',
                         #'Downward_Long-Wave_Radp_Flux_surface_Mixed_intervals_Average',
                         'Downward_Long-Wave_Radp_Flux_surface_{}_Hour_Average'.format(av),
                         #'Downward_Short-Wave_Radiation_Flux_surface_Mixed_intervals_Average',
                         'Downward_Short-Wave_Radiation_Flux_surface_{}_Hour_Average'.format(av),
                         'Planetary_Boundary_Layer_Height_surface',
                         'Precipitable_water_entire_atmosphere_single_layer',
                         #'Precipitation_rate_surface',
                         #'Precipitation_rate_surface_Mixed_intervals_Average',
                         'Precipitation_rate_surface_{}_Hour_Average'.format(av)]
        else:
            self.prms = self.prms
        av_prms = set(self.ncss.variables).intersection(set(self.prms))
        miss_prms = list(set(self.prms)-(set(self.prms).intersection(av_prms)))
        log('\n  #### Following parameters are not available in server: #### \n -->{} \n'.format('\n -->'.join(miss_prms)))
        self.prms = list(av_prms)
        self.miss_prms = list(miss_prms)
        self.query.variables(*av_prms)

    def set_query_vert_level(self):
        if self.vlev is not None:
            self.query.vertical_level(self.vlev)

    def get_data(self):
        data_format = 'netcdf'

        if not self.connected:
            if self.dset_ref == 'archive':
                self.connect_to_archive()
            else:
                self.connect_to_catalog()
        self.set_query_loc()
        self.set_query_time_range()
        self.set_query_variables()
        self.set_query_vert_level()
        self.query.accept(data_format)
        self.netcdf_data = self.ncss.get_data(self.query)
        log('\n  #### Succesful data collection!  ####\n')
        return(self.netcdf_data)
