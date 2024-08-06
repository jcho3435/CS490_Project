import datetime, time
from typing import List
import threading

_LOGIN_EXPIRY_HOURS = 24
_CHECK_ID_CACHE_INTERVAL_S = 60 * 60 # 60 minutes in seconds
_TRANSLATION_CACHE_EXPIRY_HOURS = 1
_CHECK_TRANSLATION_CACHE_INTERVAL_S = 60 * 15 # 15 minutes in seconds

class User:
    def __init__(self, token, id, login_time=datetime.datetime.now()):
        login_time = login_time.replace(microsecond=0)
        self.token = token
        self.id = id
        self.expiry = login_time + datetime.timedelta(hours=_LOGIN_EXPIRY_HOURS)
    
    def __str__(self):
        return "{" + f"Session Token: {self.token}, User ID: {self.id}, Expiry date: {self.expiry}" + "}"
    
    def __repr__(self):
        return self.__str__()
    
class Translations:
    def __init__(self, id, history: List[dict]):
        self.id = id
        self.history = history
        self.last_access = datetime.datetime.now()

    def __str__(self):
        return "{" + f"User ID: {self.id}, Last Accessed: {self.last_access}, Translations: {self.history}" + "}" 
    
    def __repr__(self):
        return self.__str__()

translation_cache = {}
id_cache = {}

id_cache_lock = threading.Lock()
translation_cache_lock = threading.Lock()

def remove_expired_login_entries():
    while True:
        now = datetime.datetime.now()
        with id_cache_lock:
            expired_keys = [key for key, value in id_cache.items() if value.expiry < now]
            for key in expired_keys:
                del id_cache[key]
        
        time.sleep(_CHECK_ID_CACHE_INTERVAL_S) 

login_expiry_thread = threading.Thread(target=remove_expired_login_entries)
login_expiry_thread.daemon = True
login_expiry_thread.start()
    
def remove_expired_translation_entries():
    while True:
        now = datetime.datetime.now()
        with translation_cache_lock:
            expired_keys = [key for key, value in translation_cache.items() if value.last_access + datetime.timedelta(hours=_TRANSLATION_CACHE_EXPIRY_HOURS) < now or not value.updated]
            for key in expired_keys:
                del translation_cache[key]
        
        time.sleep(_CHECK_TRANSLATION_CACHE_INTERVAL_S) 

translation_expiry_thread = threading.Thread(target=remove_expired_translation_entries)
translation_expiry_thread.daemon = True
translation_expiry_thread.start()