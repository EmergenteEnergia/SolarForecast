import os
import h5py
import numpy as np
import pandas as pd
from pvlib.location import Location
from pvlib import solarposition

def simple_log(*args):
    return print(*args)

def ignore (*args, **kwargs):
    pass

def parse_fcprd(s):
    if s.lower() == 'all':
        s = '3,6,9,12,15,18,21,24'
    elif s.lower() == 'none':
        s = '0'
    try:
        return [int(fc) for fc in s.split(',')]
    except:
        raise NameError('"{}" has an incorrect format. Must be a comma separated list'.format(s))

def parse_dset(s):
    if s != 'full' and s != 'best' and s != 'latest' and s != 'archive' :
        raise NameError('"{}" is not defined in the TSD Catalog as a'
                      ' dset option.'.format(s))
    else:
        return s

def parse_res(s):
    if s != '0p25' and s != '0p50':
        raise NameError('"{}" is not defined as an option for forecast'
                        'resolution.'.format(s))
    else:
        return s

def parse_outres(s):
    try:
        int(s)
        return s.lower() 
    except:
        raise NameError('"{}" invalid output resolution. Must be given in'
                        'minutes as an integer'.format(s))

def parse_dt(s):
    if s.lower() == 'none':
        return None
    else:
        dt = np.datetime64(s,'s')
        if dt.astype(str)[11:13] != '00' and dt.astype(str)[11:13] != '06' and dt.astype(str)[11:13] != '12' and dt.astype(str)[11:13] != '18':
            raise NameError('"{}" is not valid forecast runtime'.format(s))
        else:
            return dt

def parse_loc(s):
    lst = s.split(',')
    loc = {}
    try:
        for s in lst:
             loc[s.split('=')[0].lower()] = float(s.split('=')[1])
    except:
        raise NameError('the location "{}" is not in the form "lat=la1,lon=lon1",' 
                        'for a single point. Neither in the form "north=lat1,'
                        'south=lat2, east=lon1, west=lon2," for an area'
                        'or zone'.format(s))
    if set(loc.keys()) != {'lat','lon'} and set(
        loc.keys()) != {'north','south','east','west'}:
        raise NameError('labels in the location "{}" are unexpected. Please'
                        'Check'.format(s))
    return loc

def parse_prms(s):
    if s == 'all' or s=='solar':
        return s
    else:
        return s.split(',')

def parse_vlev(s):
    if s.lower() == 'none':
        return s
    else:
        return int(s)

def save_dict_to_h5items(h5file, path, dic,attrs):
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
            if 'units' in attrs[key].keys():
                h5file[path + key].attrs['units'] = attrs[key]['units']
        elif isinstance(item, dict):
            save_dict_to_h5items(h5file, path + key + '/', item,attrs[key])
        else:
            raise ValueError('Cannot save %s type'%type(item))

def createH5(data,attrs,filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    with h5py.File('{filename}'.format(filename= filename),'w') as h5f:
        save_dict_to_h5items(h5f, '/', data,attrs)

def get_netcdfAtt(data_netcdf,dset,attrs):
    for att in data_netcdf.variables[dset].ncattrs():
        attrs[att] = getattr(data_netcdf.variables[dset],att)
    return attrs

def get_netcdf_coords(data_netcdf,data,attrs):
    names = set(data_netcdf.variables).intersection({'lat','lon','latitude','longitude'})
    for n in names:
        data[n] = np. array(data_netcdf[n][:])
        attrs[n]= get_netcdfAtt(data_netcdf,n,{})
    return data,attrs

def get_coord_pos(f5,loc):
    names = set(f5['coords'].keys()).intersection({'lat','lon','latitude','longitude'})
    data = {'coords':{}}
    pos = {}
    for n in names:
        pt = loc['lat'] if 'lat' in n else 360+loc['lon']
        pixels = f5['coords'][n][:]
        arr  = np.array([np.min(pixels[np.where((pixels>pt))]),np.max(pixels[np.where(
            (pixels<pt))])])
        pos[n] = np.sort(np.append(np.where(pixels == arr[0])[0][0],np.where(
            pixels == arr[1])[0][0]))
    return(pos)

def get_coord_vals(f,data,attrs,pos):
    lat = set(pos.keys()).intersection({'lat','latitude'}).pop()
    lon = set(pos.keys()).intersection({'lon','longitude'}).pop()
    for key, item in f.items():
        if isinstance(item, h5py._hl.group.Group):
            data[key] = {}
            attrs[key] = {}
            get_coord_vals(f[key],data[key],attrs[key],pos)
        elif isinstance(item, h5py._hl.dataset.Dataset):
            if 'lat' in key:
                data[key] = item[pos[lat][0]:pos[lat][1]+1]
            elif 'lon' in key:
                data[key] = item[pos[lon][0]:pos[lon][1]+1]
            else:
                data[key] = item[pos[lat][0]:pos[lat][1]+1,pos[lon][0]:pos[lon][1]+1]
            attrs[key] = {'units':item.attrs['units']}
    return(data,attrs)

def read_csv(filename,tz,outres):
    outres = str(outres)+'Min'
    df = pd.read_csv(filename,index_col=0)
    df.index = pd.to_datetime(df.index, dayfirst = True)
    df.index = df.index.tz_localize(tz)
    df = df.rename(columns=str.lower)

    cols=set(df.columns)
    if 'radiacion' in cols:
        df.loc[df.calidad != 1, 'radiacion'] = float('NaN')
        df.loc[df.radiacion < 0, 'radiacion'] = 0
    elif 'temperatura' in cols:
        df.loc[df.calidad != 1, 'temperatura'] = float('NaN')
        df.loc[df.temperatura < 0, 'temperatura'] = 0

    times = df.index
    df.index = df.index.tz_convert('UTC').tz_localize(None)
    if outres:
        df=df.resample(outres,closed='right',label='right').mean()
    else:
        df=df.resample('Min',closed='right',label='right').mean()
    return(df,times)

def fill_dict(dic,key,dataset):
    if key in dic.keys():
        dic[key] = np.append(dic[key],dataset)
    else:
        dic[key] = dataset
    return(dic)

def get_csmodel(times,outres):
    outres = str(outres)+'Min'
    tus = Location(6.265, -75.588, 'America/Bogota', 1495,'MDE') #Torre SIATA
    solpos= solarposition.get_solarposition(times,tus.latitude,tus.longitude,tus.altitude)
    cs = tus.get_clearsky(times)

    cs.index = cs.index.tz_convert('UTC').tz_localize(None)

    if outres:
        cs=cs.resample(outres,closed='right',label='right').mean()
    else:
        cs=cs.resample('Min',closed='right',label='right').mean()

    solpos=solarposition.get_solarposition(cs.index,tus.latitude,tus.longitude,tus.altitude)
    azimuth = solpos.azimuth
    zenith_ang = solpos.apparent_zenith
    zenith_ang[zenith_ang > 90] = np.nan

    return(cs.ghi,zenith_ang,azimuth)

def create_SiataAttr(dic):
    attrs = {}
    for key in dic:
        if key == 'radiacion' or key == 'cs_ghi':
            attrs[key] = {'units':'W-m2'}
        elif key == 'zenith_ang' or key == 'azimuth':
            attrs[key] = {'units':'deg'}
        elif key == 'temperatura':
            attrs[key] = {'units':'C'}
        elif key == 'timestamp':
            attrs[key] = {'units':'UTC'}
        else:
            attrs[key] = {'units':'NA'}
    return(attrs)


def extract_dic(dic,pos1,pos2):
    for key in dic:
        dic[key] = dic[key][pos1:pos2]
    return(dic)
