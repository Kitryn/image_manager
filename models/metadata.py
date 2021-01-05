from pathlib import Path
from .dbbase import DbBase
import hashlib

class Metadata(DbBase):
    def __init__(self, db_filename):
        super().__init__(db_filename)
    
    @staticmethod
    def file_checksum(file):
        # Takes a single Path object denoting a valid file and returns md5
        hash_md5 = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def batch_get(self):
        with self.connect() as conn:
            cur = conn.execute("SELECT * FROM metadata")
            res = cur.fetchall()
            return res
    
    def batch_compare_orphans(self, file_list):
        # Takes an iterable of Path objects
        # Compares them to the db and returns list of missing files (Path objects) that are in the db
        files_in_db = self.batch_get()
        file_list_set = {file for file in file_list}
        result_set = {Path(file[1]) for file in files_in_db}
        difference = result_set - file_list_set
        return [file for file in difference]
    
    def batch_compare_new_files(self, file_list):
        # Takes an iterable of Path objects
        # Compares them to the db and returns list of files that are yet to be imported
        files_in_db = self.batch_get()
        file_list_set = {file for file in file_list}
        result_set = {Path(file[1]) for file in files_in_db}
        difference = file_list_set - result_set
        return [file for file in difference]
    
    def add_metadata_to_db(self, file_list):
        # Takes an iterable of Path objects
        # Adds fpath, fhash to metadata db
        # Warning: will throw exception on duplicate files, assumes all files are new
        metadata = [(str(file), Metadata.file_checksum(file)) for file in file_list]
        with self.connect() as conn:
            conn.executemany("INSERT INTO metadata(fpath, fhash) VALUES(?, ?)", metadata)
    
    def add_only_new_files(self, file_list):
        new_file_list = self.batch_compare_new_files(file_list)
        self.add_metadata_to_db(new_file_list)
    
    def remove_orphans(self, file_list):
        orphans = self.batch_compare_orphans(file_list)
        fpath_list = [(str(file),) for file in orphans]
        print(fpath_list)
        with self.connect() as conn:
            conn.executemany("DELETE FROM metadata WHERE fpath = ?", fpath_list)
            