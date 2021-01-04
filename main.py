import sqlite3
from pathlib import Path
import hashlib
import argparse

conn = sqlite3.connect("example.db")
OPTIONS = {
    "gallery_root": None
}

def walk_directory(root_directory):
    # Returns a tuple? of all files and their paths, excludes dotfiles and dirs starting with dot
    # This uses relative directories, can maybe expand to absolutes elsewhere if required
    def file_filter(path_obj):
        # Filter Paths we don't want, like directories or dotfiles
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
        result = cur.fetchone()
        if result: return result[1]
    return None

def set_preference(pref, val):
    with conn:
        conn.execute("INSERT INTO prefs(pref, val) VALUES(?, ?)", (pref, val))

def add_metadata_to_db(file_list):
    # Takes a iterable of Path objects of files to add
    # TODO: try/error bc it likely will shout at you if you insert duplicates
    # Prepare iterable: fpath, fhash
    metadata = [(str(file), file_checksum(file)) for file in file_list]
    
    with conn:
        conn.executemany("INSERT INTO metadata(fpath, fhash) VALUES(?, ?)", metadata)

def load_gallery():
    gr = get_preference("gallery_root")
    assert gr, "Failed to look up gallery root in preferences"
    OPTIONS["gallery_root"] = gr

def init_new_gallery(path_to_gallery):
    # Verify new path is valid
    gallery_path = Path(path_to_gallery).expanduser().resolve(strict=True)  # Throws FileNotFoundError if path does not exist
    if gallery_path.is_file(): raise Exception("Given path must be a valid directory")
    
    # DELETE ALL EXISTING DATA!
    with conn:
        conn.execute("DELETE FROM metadata")
        conn.execute("DELETE FROM tags")
        conn.execute("DELETE FROM albums")
    set_preference("gallery_root", str(gallery_path))
    

def main():
    init_db()
    args = parser.parse_args()
    
    # Before initialising the gallery, check we have a valid reference to one
    gallery_dir = get_preference("gallery_root")

    if args.directory and gallery_dir:
        # Attempted to set a directory when one already exists
        raise Exception("Attempted to set gallery root when one is already set")
    elif not gallery_dir:
        if not args.directory:
            raise Exception("Gallery root is not set!")
        init_new_gallery(args.directory)
    else:
        # gallery dir is already set
        print("Continue initialisation")
    
    load_gallery()    
    # add_metadata_to_db(walk_directory(Path(".")))

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="Root directory of image gallery")

if __name__ == "__main__":
    main()
    print("end")
    