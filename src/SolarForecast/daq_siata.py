import argparse, os
import numpy as np
from itertools import product

import gnal_fncs as fnc

def main(dt1,dt2,prms,outres,src,dst,verbose):
    global log
    log = fnc.simple_log if verbose else fnc.ignore
    log('\n  ####  Siata measurements reading for {} have started ...####\n'.format(prms))

    filenames = os.listdir(src)
    if np.datetime_as_string(dt1, unit='M') == np.datetime_as_string(dt2, unit='M'):
        dt64 = np.arange(dt1.astype('datetime64[M]'),dt1.astype('datetime64[M]')
                         + np.timedelta64(1,'M'))
    else:
        #dt64 = np.arange(dt1, dt2,dtype='datetime64[M]')
        dt64 = np.arange(dt1.astype('datetime64[M]'),dt2.astype('datetime64[M]')
                         + np.timedelta64(1,'M'))

    dic = {}
    prv_time = None
    index = None
    for idx, (dt, prm, filename) in enumerate(product(dt64, prms,filenames)):
        dt_str = ''.join((np.datetime_as_string(dt, unit='M')).split('-'))+'01'
        if prm in filename and dt_str in filename:
            tz = 'America/Bogota' #for COL
            df,times = fnc.read_csv(src+filename,tz,outres)
            dataset = df[prm].to_numpy()
            dic = fnc.fill_dict(dic,prm,dataset)
            time= [np.datetime64(dt,'s') for dt in df.index]

            if time != prv_time:
                time_str =df.index.astype(str)
                dic = fnc.fill_dict(dic,'timestamp',time_str.to_numpy())
                prv_time = time
                cs_ghi,zenith_ang,azimuth = fnc.get_csmodel(times,outres)
                dic = fnc.fill_dict(dic,'cs_ghi',cs_ghi.to_numpy())
                dic = fnc.fill_dict(dic,'zenith_ang',zenith_ang.to_numpy())
                dic = fnc.fill_dict(dic,'azimuth',azimuth.to_numpy())

    pos1 = np.where(dic['timestamp'] == np.datetime_as_string(dt1,unit='s')[:10]+time_str[0][10:])
    pos2 = np.where(dic['timestamp'] == np.datetime_as_string(dt2,unit='s')[:10]+time_str[0][10:])
    dic = fnc.extract_dic(dic,pos1[0][0],pos2[0][0])
    attrs = fnc.create_SiataAttr(dic)
    h5name = dst + np.datetime_as_string(dt1,unit='s')[:10]+'_'+np.datetime_as_string(dt2,unit='s')[:10]+'_'+outres+'min.h5'
    log('\n  ####  H5 file: {} created!   ####\n'.format(h5name))
    fnc.createH5(dic,attrs,h5name)

def parse_args():
    parser = argparse.ArgumentParser(prog='PROG',description='Data reading and'
        ' postprocessing from SIATA measurements',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-dt1','--dt1', type=fnc.parse_dt,default='None',
        help='starting date to be processed e.g:2020-07-01',required= False)

    parser.add_argument('-dt2','--dt2', type=fnc.parse_dt,default='None',
        help='delimiting date to be processed. Until this date forecast will be aquired.'
            ' e.g: 2020-07-03', required= False)

    parser.add_argument('-prms','--prms', type=fnc.parse_prms,
        help='parameters to be processed in a comma separated list.', required=False)

    parser.add_argument('-outres','--outres', type=fnc.parse_outres, default='None',
        help='output time resolution', required=False)

    parser.add_argument('-src','--src', type=str,
        help='source folder path for queried data.'
        ' e.g: /path-from-source/', required=True)

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
