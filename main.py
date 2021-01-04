import sqlite3
from pathlib import Path
import hashlib

conn = sqlite3.connect("example.db")

def walk_directory(root_directory):
    # Returns a tuple? of all files and their absolute paths, excludes dotfiles and dirs starting with dot
    # This has to use relative directories! can maybe expand to absolutes elsewhere if required
    def file_filter(path_obj):
        if not path_obj.is_file(): return False
        for parent_dir in path_obj.parents:
            if str(parent_dir.name).startswith("."): return False
        return True
    return (file for file in Path(root_directory).glob("**/[!.]*") if file_filter(file))  # this can be a generator

def init_db():
    with conn:
        with open("schema.sql") as sql_file:
            sql_as_string = sql_file.read()
        conn.executescript(sql_as_string)

def file_checksum(file):
    # Takes a single Path object denoting a file and returns the md5 string
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_preference(pref):
    # Looks up the db and returns a value for the selected pref
    with conn:
        cur = conn.execute("SELECT pref, val FROM prefs WHERE(pref=?)",(pref,))
        print(cur.fetchone())

def add_metadata_to_db(file_list):
    # Takes a iterable of Path objects of files to add
    # TODO: try/error bc it likely will shout at you if you insert duplicates
    # Prepare iterable: fname, fpath, fhash
    # TODO: probably need to change table layout to deal with dupe checksums
    metadata = [(file.name, str(file.parent), file_checksum(file)) for file in file_list]
    
    with conn:
        conn.executemany("INSERT INTO metadata(fname, fpath, fhash) VALUES(?, ?, ?)", metadata)
        

if __name__ == "__main__":
    init_db()
    # add_metadata_to_db(walk_directory(Path(".")))
    get_preference("gallery_root")
    