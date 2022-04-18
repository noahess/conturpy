import platform
import subprocess
import os
import shutil
import glob
from pathlib import Path
from .read_output import ConturResult


class ConturApplication(object):
    def __init__(self, location=os.getcwd(), timeout=0.5, executable=None):
        self.location = location
        self.timeout = timeout

        if executable is None:
            bin_path = Path(__file__).parent.joinpath('bin/')
            plat = platform.system()
            if plat == 'Windows':
                executable = bin_path.joinpath('contur.exe')
            elif plat == 'Darwin' and platform.machine() == 'arm64':
                executable = bin_path.joinpath('contur_macarm64')
            else:
                raise Exception(f"Platform {plat} is not supported")
        self.executable = executable
        self._expected_to_exist = False

    def run(self):
        assert self._exists
        return subprocess.check_output(self.executable, timeout=self.timeout, cwd=self.location)

    def _run_single_file(self, file, output_dir):
        shutil.copyfile(file, os.path.join(self.location, 'input.txt'))
        self.run()
        flag, newfile = self._move_output(like_source_fn=file, dest_folder=output_dir)
        os.remove(file)

        if flag == 1:
            return ConturResult(newfile)
        else:
            return None

    def batch_input_files(self, file_list, output_dir=os.getcwd()):
        results = []
        for file in file_list:
            results.append(self._run_single_file(file, output_dir))
        self.clean_wd()
        return results

    def batch_input_folder(self, folder, output_dir=os.getcwd()):
        results = []
        for file in glob.glob(os.path.join(folder, '*.txt')):
            results.append(self._run_single_file(file, output_dir))
        self.clean_wd()
        return results

    @staticmethod
    def _move_output(dest_fn=None, like_source_fn=None, dest_folder=None,
                     src=os.path.join(os.getcwd(), 'output.txt')):
        if not os.path.exists(src):
            return -1, None
        if like_source_fn is not None:
            dest_fn = os.path.split(like_source_fn)[-1].replace('.txt', '_result.txt')
        else:
            dest_fn = 'output.txt' if dest_fn is None else dest_fn

        dest_folder = os.getcwd() if dest_folder is None else dest_folder
        newfile = os.path.join(dest_folder, dest_fn)
        shutil.copyfile(src, newfile)

        return 1, newfile

    def clean_wd(self, wd=None):
        if wd is None:
            wd = self.location
        input_file = os.path.join(wd, 'input.txt')
        output_file = os.path.join(wd, 'output.txt')

        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

    def _exists(self):
        if not self._expected_to_exist:
            exists = os.path.exists(self.executable)
            if exists:
                self._expected_to_exist = True
                return True
            else:
                return False
        else:
            return True

    def __repr__(self):
        if self._exists():
            return f"CONTUR Executable at {self.executable}"
        else:
            return f"CONTUR Executable NOT FOUND (expected at {self.executable})"
