# pylama:ignore=C0111,W0702,W0703,E722
import logging
import time

import geocoder
import ratelim

import database as cloudant
from utilities import misc


class Geolocator:
    def __init__(self):
        self.CACHE_DB_NAME = 'geolocator_cache'  # noqa

        # Get cache db
        self.geocodes_cache = None
        self.geocodes_local_cache = []
        self.db_handle = self._get_cache_db()
        self._is_cache_db_loaded = False

    @staticmethod
    def _is_valid_coords(latlng=None):
        """Returns None when invalid coords"""
        try:
            if latlng:
                coords = [float(latlng[0]), float(latlng[1])]
                if coords:
                    return True
        except:
            pass
        return False
    
    def _get_cache_db(self):
        try:
            self.client = cloudant.get_client()
            return cloudant.create_database(self.client, self.CACHE_DB_NAME)
        except:
            pass
    
    def _load_cache_db(self):
        """Returning geocodes cache"""
        # Contains geocodes not present in cache db
        try:
            # Get all geocode hashes docs
            result = self.db_handle.all_docs(include_docs=False)
            self.geocodes_cache = result
            logging.info('[GeoLocator] Cache reload succeeded: [%s] items',
                            len(result['rows']))
            self._is_cache_db_loaded = True
        except Exception as err:
            logging.info('[GeoLocator] Cache reload failed: [%s]', err)
        return self._is_cache_db_loaded
    
    def _search_geocode(self, loc_hash):
        # 1st - ensure hash db is already loaded
        # if is not loaded - do this:
        if not self._is_cache_db_loaded and not self._load_cache_db():
            return None
    
        for geocode in self.geocodes_local_cache:
            if geocode['_id'] == loc_hash:
                return geocode['latlng']
        # if hash is in db_cache - return it
        for geocode in self.geocodes_cache['rows']:
            if geocode['id'] == loc_hash:
                return self.db_handle[loc_hash]['latlng']
        return None
        
    # 'Use get_lnglat_from_location() or get_latlng_from_location() instead')
    # def get_coords_by_location(self, loc=""):
    
    def get_latlng_from_location(self, loc=""):
        """ Returns coords from cache in db or
            from geocoder passing valid location and store it in cache """
        if not loc:
            return None
    
        loc = loc.lower().strip()
        if loc:
            loc_hash = misc.create_hash(loc)
            # Lookup for missing coords in db and new cache
            geocode_found = self._search_geocode(loc_hash)
            if geocode_found:
                return geocode_found
            result = self._get_locationiq_cords(loc, loc_hash)
    
            return result
        return None
    
    def get_lnglat_from_location(self, loc=""):
        ''' This format is expected for converters?
        Also for leaflet ??? '''
        latlng = self.get_latlng_from_location(loc)
        lnglat = [latlng[1], latlng[0]] if latlng else None
        return lnglat
    
    @ratelim.patient(2, 1)  # every 0.5
    @ratelim.patient(60, 60)
    def _get_locationiq_cords(self, loc, loc_hash=None, attempts=2):
        if not loc or attempts < 1:
            return None
        try:
            gc_res = geocoder.locationiq(loc, key="xxxxxxxx")
            if gc_res.status_code == 429:
                time.sleep(1)
    
                return self._get_locationiq_cords(loc, loc_hash, attempts - 1)
    
            if gc_res.status_code == 404:
                # try to fix ...
                names_fixes = {
                    # 404: correct
                    'newzeland': 'new zeland'
                }
                if loc in names_fixes:
                    new_loc = names_fixes[loc]
                    # new_loc, but old hash
                    return self._get_locationiq_cords(new_loc, loc_hash,
                                                        attempts - 1)
    
                logging.info('[Geolocator][%s] Not found: [%s]',
                                gc_res.status_code, loc)
                return None
    
            if gc_res.status_code != 200:
                logging.info('[Geolocator][%s] Error status code for %s',
                                gc_res.status_code, loc)
            elif Geolocator._is_valid_coords(gc_res.latlng):
                duplicates_set = {
                    item['_id'] == loc_hash
                    for item in self.geocodes_local_cache
                }
                if not any(duplicates_set):
                    # Storing new coords in unique cache
                    if not loc_hash:
                        loc_hash = misc.create_hash(loc)
                    new_coord = {
                        '_id': loc_hash,
                        'location': loc,
                        'latlng': gc_res.latlng,
                        'importance': gc_res.importance
                    }
                    if gc_res.importance < 0.2:
                        logging.warning(
                            '[Geolocator][%s] Importance low: [%.2f]', loc,
                            gc_res.importance)
                    self.geocodes_local_cache.append(new_coord)
                else:
                    logging.info('[Geolocator][Assertion] Duplicate: %s/%s',
                                    loc, loc_hash)
                return gc_res.latlng
            else:
                logging.info('[Geolocator][OK] - but not found: %s', loc)
        except:
            pass
        return None
    
    def update_cache(self):
        result = None
        if self.geocodes_local_cache:
            result = self.db_handle.bulk_docs(self.geocodes_local_cache)
            logging.info(
                '[GeoLocator:update_cache] Flushed cache, %s/%s new locations transferred',
                len(result), len(self.geocodes_local_cache))
            self.geocodes_local_cache = []
        return result