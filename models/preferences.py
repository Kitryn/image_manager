from .dbbase import DbBase

class Preferences(DbBase):
    def __init__(self, db_filename):
        super().__init__(db_filename)
        
    def get_preference(self, pref):
        with self.connect() as conn:
            cur = conn.execute("SELECT pref, val FROM prefs WHERE (pref=?)", (pref,))
            result = cur.fetchone()
            if result: return result[1]
        return None
    
    def set_preference(self, pref, val):
        with self.connect() as conn:
            conn.execute("INSERT INTO prefs(pref, val) VALUES(?, ?) ON CONFLICT(pref) DO UPDATE SET val = ?", (pref, val, val))
    
    @property
    def gallery_root(self):
        try:
            return self._gallery_root
        except AttributeError:
            self._gallery_root = self.get_preference("gallery_root")
            return self._gallery_root
    
    @gallery_root.setter
    def gallery_root(self, val):
        print(val)
        self.set_preference("gallery_root", val)
        self._gallery_root = val