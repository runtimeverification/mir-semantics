from pathlib import Path


def get_py_root() -> Path:
    return Path(__file__).parent.parent.parent


def default_def(llvm: bool) -> Path:
    ext = 'llvm.def' if llvm else 'haskell.def'
    path = get_py_root() / ext

    try:
        with open(path, 'r+') as def_file:
            def_location = def_file.readline().strip('\n')
            return Path(def_location)
    except FileNotFoundError as err:
        print(f'File {ext!r} not found, try running: make build\n', flush=True)
        raise (err)
