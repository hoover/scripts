from pathlib import Path

def organize_file(item, out_path):
    hash = item.stem
    assert len(hash) == 32
    folder = out_path / hash[:2] / hash[2:4]
    folder.mkdir(parents=True, exist_ok=True)
    organized_item = folder / item.name
    if organized_item.exists():
        print("item exists, overwriting", hash)
    item.rename(organized_item)

def organize(in_path, out_path):
    if in_path.is_dir():
        for item in in_path.iterdir():
            organize(item, out_path)
    else:
        organize_file(in_path, out_path)

if __name__ == '__main__':
    import sys
    [in_path, out_path] = [Path(p) for p in sys.argv[1:]]
    organize(in_path, out_path)
