import sqlite3
from pathlib import Path
import hashlib
import argparse
from models.metadata import Metadata
from models.preferences import Preferences

def walk_directory(root_directory):
    # Returns a list of all files and their paths, excludes dotfiles and dirs starting with dot
    def file_filter(path_obj):
        # Filter Paths we don't want, like directories or dotfiles
        if not path_obj.is_file(): return False
        for parent_dir in path_obj.parents:
            if str(parent_dir.name).startswith("."): return False
        return True

    return [file for file in Path(root_directory).glob("**/[!.]*") if file_filter(file)]
    
def get_absolute_dir(path):
    # Verify new path is valid
    gallery_path = Path(path).expanduser().resolve(strict=True)  # Throws FileNotFoundError if path does not exist
    if gallery_path.is_file(): raise Exception("Given path must be a valid directory")
    
    return str(gallery_path)
    
def init_new_gallery(db):
    # DELETE ALL EXISTING DATA!
    with db.connect() as conn:
        conn.execute("DELETE FROM metadata")
        conn.execute("DELETE FROM tags")
        conn.execute("DELETE FROM albums")

def load_gallery(db, gallery_path):
    file_list = walk_directory(gallery_path)
    db.add_only_new_files(file_list)
    db.remove_orphans(file_list)

def main():
    db = Metadata("example.db")
    pref = Preferences("example.db")
    args = parser.parse_args()
    
    # Before initialising the gallery, check we have a valid reference to one
    if args.directory and pref.gallery_root:
        raise Exception("Attempted to set gallery root when it is already set")
    elif not pref.gallery_root:
        if not args.directory:
            raise Exception("Gallery root is not set! Run with args -d DIRECTORY to set a gallery directory")
        new_path = get_absolute_dir(args.directory)
        print(new_path)
        pref.gallery_root = new_path
        init_new_gallery(db)
    else:
        # Gallery root is already set. We may as well verify it's a valid dir
        get_absolute_dir(pref.gallery_root)

    load_gallery(db, pref.gallery_root)    

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="Root directory of image gallery")

if __name__ == "__main__":
    main()
    print("end")
    