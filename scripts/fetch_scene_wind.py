"""Join an ERA5 10 m wind estimate to the real SAR tile center (not to SOS).

Open-Meteo archive is an intermediary for ERA5, explicitly selected instead of
the blended default. Nearest grid cell, no elevation downscaling; UTC times.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
from sentinel_calibration_demo import bilinear_numpy

ROOT = Path(__file__).resolve().parents[1]


def wind_vector(speed, direction):
    """Meteorological FROM degrees clockwise from north -> east/north m/s."""
    radians = math.radians(direction)
    return np.array([-speed*math.sin(radians), -speed*math.cos(radians)])


def main():
    tile = json.loads((ROOT/'docs/management/sentinel_window_audit.json').read_text())
    directory = (ROOT/tile['file']).parent
    annotation_path = directory/'annotation/iw-vv.xml'
    metadata = json.loads((ROOT/'docs/management/sentinel_metadata_audit.json').read_text())
    receipt = next(r for r in metadata['files'] if r.get('file','').endswith('/annotation/iw-vv.xml'))
    assert hashlib.sha256(annotation_path.read_bytes()).hexdigest()==receipt['sha256']
    points = ET.parse(annotation_path).findall('.//geolocationGridPoint')
    gy = sorted({int(p.findtext('line')) for p in points})
    gx = sorted({int(p.findtext('pixel')) for p in points})
    mapping = {(int(p.findtext('line')),int(p.findtext('pixel'))):p for p in points}
    assert len(mapping)==len(gy)*len(gx)
    center = [origin+(size-1)/2 for origin,size in zip(tile['window_origin_line_pixel'],tile['tile_shape'])]
    def interpolate(field, transform=float):
        values = np.array([[transform(mapping[(y,x)].findtext(field)) for x in gx] for y in gy])
        return float(bilinear_numpy(gy,gx,values,[center[0]],[center[1]])[0,0])
    lat,lon = interpolate('latitude'),interpolate('longitude')
    base = datetime.fromisoformat(points[0].findtext('azimuthTime')).replace(tzinfo=timezone.utc)
    seconds = interpolate('azimuthTime',lambda s:(datetime.fromisoformat(s).replace(tzinfo=timezone.utc)-base).total_seconds())
    moment = base+timedelta(seconds=seconds)
    params={'latitude':f'{lat:.7f}','longitude':f'{lon:.7f}',
        'start_date':moment.date().isoformat(),'end_date':moment.date().isoformat(),
        'hourly':'wind_speed_10m,wind_direction_10m','models':'era5','timezone':'GMT',
        'wind_speed_unit':'ms','cell_selection':'nearest','elevation':'nan'}
    url='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(url,timeout=45) as response:
        raw=response.read(1_000_001)
    assert len(raw)<=1_000_000
    data=json.loads(raw)
    assert data['utc_offset_seconds']==0
    assert data['hourly_units']['wind_speed_10m']=='m/s'
    times=[datetime.fromisoformat(s).replace(tzinfo=timezone.utc) for s in data['hourly']['time']]
    left=max(i for i,t in enumerate(times) if t<=moment)
    assert left+1<len(times)
    weight=(moment-times[left]).total_seconds()/(times[left+1]-times[left]).total_seconds()
    values=[]
    for index in (left,left+1):
        speed=data['hourly']['wind_speed_10m'][index]
        direction=data['hourly']['wind_direction_10m'][index]
        assert speed is not None and direction is not None and speed>=0
        assert 0<=direction<=360
        values.append({'time_utc':times[index].isoformat(),'speed_m_s':speed,'from_degrees':direction})
    vector=(1-weight)*wind_vector(values[0]['speed_m_s'],values[0]['from_degrees'])+weight*wind_vector(values[1]['speed_m_s'],values[1]['from_degrees'])
    speed=float(np.linalg.norm(vector))
    direction=math.degrees(math.atan2(-vector[0],-vector[1]))%360 if speed>0 else None
    radians=np.deg2rad([lat,lon,data['latitude'],data['longitude']])
    la,lo,lb,lp=radians
    hav=math.sin((lb-la)/2)**2+math.cos(la)*math.cos(lb)*math.sin((lp-lo)/2)**2
    distance=6371*2*math.asin(math.sqrt(min(1,hav)))
    raw_path=directory/'era5_wind_raw.json'; raw_path.write_bytes(raw)
    result={'scene':tile['scene'],'annotation_sha256':receipt['sha256'],
        'tile_center_line_pixel':center,'sar_center_utc':moment.isoformat(),
        'requested_lat_lon':[lat,lon],'returned_grid_lat_lon':[data['latitude'],data['longitude']],
        'grid_center_distance_km':distance,'request_url':url,'request_parameters':params,
        'source':'ERA5 via Open-Meteo archive; nominal 0.25 degree hourly reanalysis',
        'raw_file':raw_path.relative_to(ROOT).as_posix(),'raw_sha256':hashlib.sha256(raw).hexdigest(),
        'bracketing_hours':values,'temporal_weight':weight,'method':'Linear interpolation of u/v vectors, not of circular direction',
        'u_east_m_s':float(vector[0]),'v_north_m_s':float(vector[1]),'speed_m_s':speed,'from_degrees':direction,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limitations':['Single coarse reanalysis grid cell, not SAR pixel-scale wind or field observation',
            'API speed/direction are rounded; reconstructed vectors have rounding error',
            'No classifier or threshold changed using this wind','No wind linkage to SOS images','No proof that a dark SAR region is caused by low wind']}
    (ROOT/'results/physical/wind.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
