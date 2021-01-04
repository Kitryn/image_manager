import sqlite3
from pathlib import Path

conn = sqlite3.connect("example.db")

def walk_directory(root_directory):
    # Returns a tuple? of all files and their absolute paths, excludes dotfiles and dirs starting with dot
    # This has to use relative directories! can maybe expand to absolutes elsewhere if required
    def file_filter(path_obj):
        if not path_obj.is_file(): return False
        for parent_dir in path_obj.parents:
            if str(parent_dir.name).startswith("."): return False
        return True
    return (file for file in Path(root_directory).glob("**/[!.]*") if file_filter(file))

def init_db():
    with conn:
        with open("schema.sql") as sql_file:
            sql_as_string = sql_file.read()
        conn.executescript(sql_as_string)

def add_metadata_to_db():
    pass

if __name__ == "__main__":
    init_db()
    for file in walk_directory(Path(".")):
        print(file)
    