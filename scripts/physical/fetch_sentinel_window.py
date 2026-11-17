"""Download one native central TIFF tile by HTTP range, not the entire SAR scene.

This physical-preprocessing sample has no oil label. It is not a SOS patch or
an independently annotated detection test. Download budget is capped at 20 MB.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import hashlib
import io
import json
import math
import re
import urllib.request
from pathlib import Path

import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parents[2]


class RangeReader(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos, self.total, self.downloaded = url, 0, None, 0
        self.cache = {}
        self.requests = []
        self._range(0, 16384)

    def _range(self, offset, size):
        key = (offset, size)
        if key in self.cache:
            return self.cache[key]
        if self.downloaded + size > 20_000_000:
            raise ValueError('20 MB metadata/tile download budget exceeded')
        req = urllib.request.Request(self.url, headers={'Range':f'bytes={offset}-{offset+size-1}'})
        with urllib.request.urlopen(req, timeout=45) as response:
            match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', response.headers.get('Content-Range',''))
            if response.status != 206 or not match:
                raise ValueError('Server did not honor byte range; refusing full-scene download')
            start, end, total = map(int, match.groups())
            if start != offset or end != offset+size-1:
                raise ValueError('Server returned a different range')
            if self.total is not None and total != self.total:
                raise ValueError('Remote file size changed')
            self.total = total
            raw = response.read(size+1)
        if len(raw)!=size: raise ValueError('Truncated range')
        self.downloaded += len(raw)
        self.cache[key] = raw
        self.requests.append({'offset':offset,'bytes':size,'sha256':hashlib.sha256(raw).hexdigest()})
        return raw

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        position = offset if whence==0 else self.pos+offset if whence==1 else self.total+offset
        if position<0: raise ValueError('Negative seek')
        self.pos = position
        return self.pos
    def read(self, size=-1):
        size = self.total-self.pos if size<0 else min(size,self.total-self.pos)
        if size<=0: return b''
        # Reuse a containing metadata range instead of tiny HTTP requests.
        for (start,length), raw in self.cache.items():
            if start<=self.pos and self.pos+size<=start+length:
                result = raw[self.pos-start:self.pos-start+size]
                self.pos += size
                return result
        result = self._range(self.pos,size)
        self.pos += size
        return result
    def readinto(self, buffer):
        raw = self.read(len(buffer)); buffer[:len(raw)] = raw
        return len(raw)


def main():
    audit = json.loads((ROOT/'docs/management/sentinel_metadata_audit.json').read_text())
    scene = audit['scene']
    directory = ROOT/'data/sentinel_metadata'/scene
    product = json.loads((directory/'productInfo.json').read_text())
    assert 'measurement/iw-vv.tiff' in product['filenameMap'].values()
    url = 'https://sentinel-s1-l1c.s3.amazonaws.com/'+product['path']+'/measurement/iw-vv.tiff'
    reader = RangeReader(url)
    with tifffile.TiffFile(reader) as tif:
        page = tif.pages[0]
        height, width = page.shape
        expected = audit['original_image_dimensions']
        assert (height,width)==(expected['numberOfLines'],expected['numberOfSamples'])
        assert page.is_tiled and page.samplesperpixel==1
        tile_h, tile_w = page.tilelength, page.tilewidth
        row, col = (height//2)//tile_h, (width//2)//tile_w
        index = row*math.ceil(width/tile_w)+col
        offset, count = page.dataoffsets[index], page.databytecounts[index]
        encoded = reader._range(offset,count)
        decoded, position, shape = page.decode(encoded,index)
        tile = np.asarray(decoded)[0,:,:,0]
        assert position[2:4]==(row*tile_h,col*tile_w)
        assert tile.shape==(tile_h,tile_w)
        destination = directory/'central_vv_dn.npy'
        np.save(destination,tile,allow_pickle=False)
        result = {'scene':scene,'source_url':url,'remote_bytes':reader.total,
                  'downloaded_bytes':reader.downloaded,'ranges':reader.requests,
                  'original_shape':[height,width],'window_origin_line_pixel':[row*tile_h,col*tile_w],
                  'tile_shape':list(tile.shape),'tile_dtype':str(tile.dtype),
                  'tile_min':int(tile.min()),'tile_max':int(tile.max()),
                  'file':destination.relative_to(ROOT).as_posix(),
                  'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
                  'oil_ground_truth_available':False,'sos_patch_mapping_available':False,
                  'calibration_applied':False,'incidence_normalization_applied':False}
    (ROOT/'docs/management/sentinel_window_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
