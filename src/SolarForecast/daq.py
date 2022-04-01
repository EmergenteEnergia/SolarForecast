import argparse
import numpy as np
from itertools import product

import gnal_fncs as fnc
from GFS_model import GFSmodel


def main(dset_ref,res,fc_prd,dt1,dt2,loc,prms,vlev,dst,verbose):
    global log
    log = fnc.simple_log if verbose else fnc.ignore
    log('\n  ####  GFS daq for {} have started ...  ####\n'.format(dset_ref))

    dt1 = dt1 if dset_ref != 'latest' else np.datetime64('now')
    dtend = dt2
    fc_prd = [0] if dset_ref != 'archive' else fc_prd
    if dset_ref == 'archive' and dt2:
        dt64 = np.arange(dt1, dt2,dtype='datetime64[6h]')
        dt2 = None
    else:
        dt64 = [dt1]

    errs = []
    data = {}
    attrs = {}
    cdt = dt1
    for idx, (dt, fc) in enumerate(product(dt64, fc_prd)):
        datetimestr = np.datetime_as_string(cdt, unit='s')[:13]
        if np.datetime_as_string(dt, unit='D') != np.datetime_as_string(cdt, unit='D'):
            try:
                data['coords'],attrs['coords'] = fnc.get_netcdf_coords(data_netcdf,{},{})
                fnc.createH5(data,attrs,dst+'{}_{}_COL.h5'.format(datetimestr.split('T')[0],res))
                log('\n  ####  Finished for {}  ####\n'.format(datetimestr.split('T')[0]))
                data = {}
                attrs = {}
            except Exception as e:
                errs.append('{} --> {}'.format(datetimestr,e))

        datetimestr = np.datetime_as_string(dt, unit='s')[:13]
        gr = datetimestr.split('T')[1]+'UTC'
        key = '{:02d}H'.format(fc) if dset_ref == 'archive' else dset_ref
        data[gr] = {} if not gr in data.keys() else data[gr]
        data[gr][key] = {} if not key in data[gr] else data[gr][key]
        attrs[gr] = {} if not gr in attrs.keys() else attrs[gr]
        attrs[gr][key] = {} if not key in attrs[gr] else attrs[gr][key]
        try:
            model = GFSmodel(dset_ref,res,fc,dt,dt2,loc,prms,vlev,verbose)
            data_netcdf = model.get_data()
            for dset in model.prms:
                attrs[gr][key][dset] = fnc.get_netcdfAtt(data_netcdf,dset,{})
                data[gr][key][dset] = np.array(data_netcdf[dset][:])[0]
                dset_shape = np.shape(np.array(data_netcdf[dset][:])[0])
            for m_dset in model.miss_prms:
                attrs[gr][key][m_dset] = {'units':'NA'}
                arr_init = np.zeros(dset_shape)
                arr_init[:] = np.nan
                data[gr][key][m_dset] = arr_init
        except Exception as e:
            errs.append('{} --> {}'.format(datetimestr,e))
        cdt = dt

    try:
        data['coords'],attrs['coords'] = fnc.get_netcdf_coords(data_netcdf,{},{})
        fstr = datetimestr if dset_ref != 'archive' else datetimestr.split('T')[0]
        fnc.createH5(data,attrs,dst+'{}_{}_COL.h5'.format(fstr,res))
        log('\n  ####  Finished for {}  ####\n'.format(datetimestr.split('T')[0]))
    except Exception as e:
        errs.append('{} --> {}'.format(datetimestr,e))

    if errs:
        dates = np.datetime_as_string(dt1,
                                      unit='D')+'_'+np.datetime_as_string(dtend, unit='D')
        with open(dst+'errs{}_{}'.format(dset_ref,dates),'w') as out:
            out.write('\n'.join(errs))
        log('\n  ####  Finished -  Erros found in data acquisition...  ####\n'.format(datetimestr))

def parse_args():
    parser = argparse.ArgumentParser(prog='PROG',description='Data adquisition of'
        ' GFS meteo data. It access the remote data from the THREDDS data server.'
        '  Output are netcdf files with queried forecast data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-dset_ref','--dset_ref', type=fnc.parse_dset,
        help='Reference of dataset from the TDS Catalog to be processed. Options: "full",'
        ' "best","latest","archive"', required=True)

    parser.add_argument('-res','--res', type=fnc.parse_res,
        help='Forecast resoultion. 0.25 degree resolution forecasts are made'
        ' every hour. Forecasts with 0.50 degree resolution are made every 3 hours.'
        ' Options: "0p25", "0p50"', required=True)

    parser.add_argument('-fc_prd','--fc_prd', type=fnc.parse_fcprd,default='all',
        help='Forecast times of product as a comma separated list'
        ' Options:from "0", "3",..., until "384"', required=False)

    parser.add_argument('-dt1','--dt1', type=fnc.parse_dt,default='None',
        help='starting date to be processed, including desired forecast time'
        ' (if applicable). e.g:2020-07-01T00',required= False)

    parser.add_argument('-dt2','--dt2', type=fnc.parse_dt,default='None',
        help='delimiting date to be processed, including desired forecast time'
            ' (if applicable). Until this date forecast will be aquired.'
            ' e.g: 2020-07-03T00', required= False)

    parser.add_argument('-loc','--loc', type=fnc.parse_loc,
        help='Location. If it is single point, enter the decimal coordinates'
        ' in a comma separated list (e.g: lat=lat1,lon=lon1).'
        ' If it is an area or zone, enter the cardinal extension in'
        ' decimal coordinates as a list. (e.g: north=lat1, south=lat2,'
        ' east=lon1, west=lon2)', required=True)

    parser.add_argument('-prms','--prms', type=fnc.parse_prms, default='all',
        help='parameters to be processed in a comma separated list.'
        ' Use "all" for all parameters. Use "solar" for default parameters used'
        ' in solar irradiance forecasting. eg: "all"', required=False)

    parser.add_argument('-vlev','--vlev', type=fnc.parse_vlev, default='None',
        help='vertical altitude for queried forecasted data.', required=False)

    parser.add_argument('-dst','--dst', type=str,
        help='destination absolute folder path for queried data.'
        ' filename will include timerange, resolution and location.'
        ' e.g: /path-to-output/timerange_resolution_location_raw.h5.', required=True)

    parser.add_argument('-v','--verbose', action='store_true', default=False,
            help='verbose run. Default: False',required=False)

    args = parser.parse_args()

    if args.dset_ref == 'archive':
        args.res = '0p25'
        if args.dt1 is None:
            raise argparse.ArgumentTypeError('-dt1/--dt1 argument is required in the form:'
                                           ' YYYY-MM-DDTHH') 
    if args.dset_ref != 'latest' and args.dset_ref != 'archive' and  (
        args.dt1 is None or args.dt2 is None):
        raise argparse.ArgumentTypeError('the following arguments are required:'
                                         ' -dt1/--dt1, -dt2/--dt2')
    main(**vars(args))

if __name__ == '__main__':

    parse_args()
