import argparse
import numpy as np
from itertools import product

import gnal_fncs as fnc
from GFS_model import GFSmodel


def main(dt1,dt2,loc,dst,verbose):
    global log
    log = fnc.simple_log if verbose else fnc.ignore
    log('\n  ####  GFS daq for MDE archive have started ...  ####\n')
    fc_prd = fnc.parse_fcprd('all')

    if  dt2:
        dt64 = np.arange(dt1, dt2,dtype='datetime64[6h]')
        dt2 = None
    else:
        dt64 = [dt1]

    errs = []
    logs = []
    data = {}
    attrs = {}
    cdt = dt1
    for idx, (dt, fc) in enumerate(product(dt64, fc_prd)):
        if cdt.astype('datetime64[D]') != dt.astype('datetime64[D]'):
            logs.append('Data from {} acquired in {} seconds'.format(
                cdt.astype('datetime64[D]'),np.datetime64('now')-act))
            act = np.datetime64('now')
        elif dt.astype(object).hour ==0:
            act = np.datetime64('now')

        datetimestr = np.datetime_as_string(dt, unit='s')[:13]
        timestamp = (dt + np.timedelta64(int(fc),'h')).astype('datetime64[s]').astype(int)
        gr = datetimestr.split('T')[1]+'UTC'
        data[gr] = {} if not gr in data.keys() else data[gr]
        data[gr]['timestamp'] = np.array([timestamp]) if not 'timestamp' in data[
            gr].keys() else np.append(data[gr]['timestamp'], timestamp)
        attrs[gr] = {} if not gr in attrs.keys() else attrs[gr]
        attrs[gr]['timestamp'] ={'units':'EPOCH'}
        try:
            model = GFSmodel(fc,dt,loc,verbose)
            data_netcdf = model.get_data()
            for dset in model.prms:
                vals = np.array([data_netcdf[dset][:][0]])
                dset_size = len(vals)
                if dset in data[gr].keys():
                    data[gr][dset] = np.append(data[gr][dset],vals)
                else:
                    attrs[gr][dset] = fnc.get_netcdfAtt(data_netcdf,dset,{})
                    data[gr][dset] = np.array(vals)
            for m_dset in model.miss_prms:
                if m_dset not in data[gr].keys():
                    attrs[gr][m_dset] = {'units':'NA'}
                    data[gr][m_dset] = np.zeros(dset_size) * np.nan

            with open(dst+'logs','w') as out:
                out.write('\n'.join(logs))

        except Exception as e:
            errs.append('{} --> {}'.format(datetimestr,e))
        cdt = dt


    try:
        data['coords'],attrs['coords'] = fnc.get_netcdf_coords(data_netcdf,{},{})
        fstr = np.datetime_as_string(dt1, unit='D') +'_'+ datetimestr.split('T')[0]
        fnc.createH5(data,attrs,dst+'{}_0p25_MDE.h5'.format(fstr))
        log('\n  ####  Finished for {}  ####\n'.format(datetimestr.split('T')[0]))
        print('fertig:',np.datetime64('now')-act)
    except Exception as e:
        errs.append('{} --> {}'.format(datetimestr,e))

    if errs:
        dates = np.datetime_as_string(dt1,
                                      unit='D')+'_'+np.datetime_as_string(dt, unit='D')
        with open(dst+'errs_{}'.format(dates),'w') as out:
            out.write('\n'.join(errs))
        print('\n  ####  Finished -  Erros found in data acquisition...  ####\n'.format(datetimestr))

def parse_args():
    parser = argparse.ArgumentParser(prog='PROG',description='Data adquisition of'
        ' GFS meteo data. It access the remote data from the THREDDS data server.'
        '  Output are netcdf files with queried forecast data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

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

    parser.add_argument('-dst','--dst', type=str,
        help='destination absolute folder path for queried data.'
        ' filename will include timerange, resolution and location.'
        ' e.g: /path-to-output/timerange_resolution_location_raw.h5.', required=True)

    parser.add_argument('-v','--verbose', action='store_true', default=False,
            help='verbose run. Default: False',required=False)

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':

    parse_args()
