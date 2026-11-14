"""Attach explicit ERA5 10 m wind to each tile's location and acquisition time.

Context only: wind is not used to alter labels, eligibility or model selection here.
"""
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
from scipy.interpolate import interp1d

from audit_cantarell_source import ROOT, REVISION
from fetch_scene_wind import wind_vector
from map_cantarell_native_grid import interpolate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tile_times(samples, meta):
    path = ROOT/meta['files'][0]['file']
    if sha(path)!=meta['files'][0]['sha256']:
        raise ValueError('Annotation hash mismatch')
    points = ET.parse(path).findall('.//geolocationGridPoint')
    y = np.array(sorted({int(p.findtext('line')) for p in points}))
    x = np.array(sorted({int(p.findtext('pixel')) for p in points}))
    base = datetime.fromisoformat(points[0].findtext('azimuthTime')).replace(tzinfo=timezone.utc)
    grids = {}
    for name in ['latitude','longitude','azimuthTime']:
        def parse(text):
            return (datetime.fromisoformat(text).replace(tzinfo=timezone.utc)-base).total_seconds() if name=='azimuthTime' else float(text)
        lookup = {(int(p.findtext('line')),int(p.findtext('pixel'))):parse(p.findtext(name)) for p in points}
        grids[name] = np.array([[lookup[r,c] for c in x] for r in y])
    result,errors = [],[]
    for sample in samples:
        west,south,east,north = sample['bounds_wsen']
        lat,lon = (south+north)/2,(west+east)/2
        r,c = np.array([float(np.median(y))]),np.array([float(np.median(x))])
        for _ in range(20):
            la,a,b = interpolate(y,x,grids['latitude'],r,c)
            lo,d,e = interpolate(y,x,grids['longitude'],r,c)
            det = a*e-b*d
            if abs(det[0])<1e-16:
                raise ValueError('Singular center geolocation')
            dr,dc = (e*(la-lat)-b*(lo-lon))/det,(a*(lo-lon)-d*(la-lat))/det
            r-=dr
            c-=dc
            if max(abs(dr[0]),abs(dc[0]))<1e-7:
                break
        else:
            raise ValueError('Center geolocation failed')
        if r[0]<y[0] or r[0]>y[-1] or c[0]<x[0] or c[0]>x[-1]:
            errors.append({'sample':sample['sample'],'group':sample['group'],'error':'Center outside geolocation support; no acquisition time invented'})
            continue
        seconds = interpolate(y,x,grids['azimuthTime'],r,c)[0][0]
        moment = base+timedelta(seconds=float(seconds))
        result.append({'sample':sample['sample'],'latitude':lat,'longitude':lon,'moment_utc':moment.isoformat(),
                       'center_native_line_pixel':[float(r[0]),float(c[0])]})
    return result,errors


def main():
    folder = ROOT/'docs/management'
    protocol_path = folder/'cantarell_data_protocol_v1.json'
    protocol = json.loads(protocol_path.read_text())
    inventory_path = folder/'cantarell_full_inventory.json'
    if sha(inventory_path)!=protocol['inventory_sha256']:
        raise ValueError('Inventory changed after protocol freeze')
    inventory = json.loads(inventory_path.read_text())
    meta_path = folder/'cantarell_physical_metadata_audit.json'
    metadata = json.loads(meta_path.read_text())
    if metadata['protocol_sha256']!=sha(protocol_path) or not metadata['complete']:
        raise ValueError('Physical metadata binding failed')
    by_group = defaultdict(list)
    for sample in inventory['samples']:
        by_group[sample['group']].append(sample)
    raw_dir = ROOT/'.cache/cantarell_source'/REVISION/'era5'
    raw_dir.mkdir(parents=True,exist_ok=True)
    results,errors,receipts = [],[],[]
    for meta in metadata['results']:
        group = meta['group']
        try:
            centers,center_errors = tile_times(by_group[group],meta)
            errors.extend(center_errors)
            if not centers:
                continue
            moments = [datetime.fromisoformat(r['moment_utc']) for r in centers]
            params = {'latitude':','.join(f"{r['latitude']:.7f}" for r in centers),
                      'longitude':','.join(f"{r['longitude']:.7f}" for r in centers),
                      'start_date':min(moments).date().isoformat(),
                      'end_date':(max(moments).date()+timedelta(days=1)).isoformat(),
                      'hourly':'wind_speed_10m,wind_direction_10m','models':'era5','timezone':'GMT',
                      'wind_speed_unit':'ms','cell_selection':'nearest','elevation':','.join(['nan']*len(centers))}
            url = 'https://archive-api.open-meteo.com/v1/archive?'+urlencode(params)
            key = hashlib.sha256(url.encode()).hexdigest()
            path = raw_dir/f'{group}_{key}.json'
            if not path.exists():
                with urlopen(url,timeout=45) as response:
                    raw = response.read(2_000_001)
                if len(raw)>2_000_000:
                    raise ValueError('ERA5 response too large')
                json.loads(raw)
                path.write_bytes(raw)
            batch = json.loads(path.read_text())
            if isinstance(batch,dict):
                batch = [batch]
            if len(batch)!=len(centers):
                raise ValueError('ERA5 location response count mismatch')
            receipt = {'group':group,'url':url,'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
                       'query_location_order':[r['sample'] for r in centers]}
            receipts.append(receipt)
            group_results = []
            for index,(center,moment,data) in enumerate(zip(centers,moments,batch)):
                if data.get('location_id',0)!=index:
                    raise ValueError('ERA5 response location order mismatch')
                if data['utc_offset_seconds']!=0 or data['hourly_units']['wind_speed_10m']!='m/s':
                    raise ValueError('ERA5 timezone/unit mismatch')
                times = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in data['hourly']['time']]
                left = max(i for i,t in enumerate(times) if t<=moment)
                if left+1>=len(times):
                    raise ValueError('Wind time is not bracketed')
                vectors,hours = [],[]
                for i in [left,left+1]:
                    speed,direction = data['hourly']['wind_speed_10m'][i],data['hourly']['wind_direction_10m'][i]
                    if speed is None or direction is None or not np.all(np.isfinite([speed,direction])) or speed<0 or not 0<=direction<=360:
                        raise ValueError('Invalid wind value')
                    vectors.append(wind_vector(speed,direction))
                    hours.append({'utc':times[i].isoformat(),'speed_m_s':speed,'from_degrees':direction})
                weight = (moment-times[left]).total_seconds()/(times[left+1]-times[left]).total_seconds()
                vector = (1-weight)*vectors[0]+weight*vectors[1]
                reference = interp1d([0.,1.],np.array(vectors),axis=0)(weight)
                if not np.allclose(vector,reference,rtol=1e-12,atol=1e-12):
                    raise ValueError('Wind interpolation reference mismatch')
                la,lo,lb,lp = np.deg2rad([center['latitude'],center['longitude'],data['latitude'],data['longitude']])
                hav = math.sin((lb-la)/2)**2+math.cos(la)*math.cos(lb)*math.sin((lp-lo)/2)**2
                speed = float(np.linalg.norm(vector))
                group_results.append({**center,'group':group,'scene':meta['scene'],'response_index':index,
                                      'response_location_id':data.get('location_id'),'grid_lat_lon':[data['latitude'],data['longitude']],
                                      'grid_center_distance_km':6371*2*math.asin(math.sqrt(min(1,hav))),
                                      'bracketing_hours':hours,'weight':weight,'u_east_m_s':float(vector[0]),
                                      'v_north_m_s':float(vector[1]),'speed_m_s':speed,
                                      'from_degrees':math.degrees(math.atan2(-vector[0],-vector[1]))%360 if speed>0 else None,
                                      'numpy_scipy_max_abs_error':float(np.max(np.abs(vector-reference)))})
            results.extend(group_results)
            print(f'Joined ERA5 {group}: {len(group_results)} tiles',flush=True)
        except Exception as exc:
            errors.append({'group':group,'error':f'{type(exc).__name__}: {exc}'})
            print(f'ERA5 {group}: {errors[-1]["error"]}',flush=True)
    audit = {'protocol_sha256':sha(protocol_path),'metadata_sha256':sha(meta_path),'script_sha256':sha(Path(__file__)),
             'source_documentation':'https://open-meteo.com/en/docs/historical-weather-api',
             'source':'Explicit ERA5 via Open-Meteo; hourly 0.25-degree reanalysis, nearest cell, no elevation downscaling.',
             'expected_samples':len(inventory['samples']),'joined_samples':len(results),'complete':len(results)==len(inventory['samples']) and not errors,
             'receipts':receipts,'results':results,'errors':errors,
             'limits':['Reanalysis grid wind is not a measured SAR-pixel wind or cause-specific look-alike label.',
                       'Rounded API speed/direction converted to u/v and linearly interpolated in UTC.',
                       'No wind-based label edits, sample exclusions, model selection or test scoring.']}
    (folder/'cantarell_wind_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:audit[k] for k in ['joined_samples','complete','errors']},indent=2))


if __name__=='__main__':
    main()
