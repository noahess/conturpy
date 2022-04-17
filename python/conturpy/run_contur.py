import platform
import subprocess
import os
import shutil
import glob
from .read_output import ConturResult


class ConturApplication(object):
    def __init__(self, location=os.getcwd(), timeout=0.5, executable=None):
        self.location = location
        self.timeout = timeout

        if executable is None:
            plat = platform.system()
            if plat == 'Windows':
                executable = 'contur.exe'
            elif plat == 'Darwin':
                executable = 'contur'
            else:
                raise Exception(f"Platform {plat} is not supported")
        self.executable = executable
        self._expected_to_exist = False

    def run(self):
        assert self._exists
        return subprocess.check_output(self.path, timeout=self.timeout)

    def batch_input_files(self, file_list, output_dir=os.getcwd()):
        results = []
        for file in file_list:
            shutil.copyfile(file, os.path.join(self.location, 'input.txt'))
            self.run()
            flag, newfile = self._move_output(like_source_fn=file, dest_folder=output_dir)
            
            if flag == 1:
                results.append(ConturResult(newfile))
            else:
                results.append[None]
            os.remove(file)
        return results


    def batch_input_folder(self, folder, output_dir=os.getcwd()):
        results = []
        for file in glob.glob(os.path.join(folder, '*.txt')):
            shutil.copyfile(file, os.path.join(self.location, 'input.txt'))
            self.run()
            flag, newfile = self._move_output(like_source_fn=file, dest_folder=output_dir)

            if flag == 1:
                results.append(ConturResult(newfile))
            else:
                results.append[None]
            os.remove(file)
        return results

    def _move_output(self, dest_fn=None, like_source_fn=None, dest_folder=None, src=os.path.join(os.getcwd(), 'output.txt')):
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

    @property
    def path(self):
        return os.path.join(self.location, self.executable)

    def clean_wd(self, wd=os.getcwd()):
        input_file = os.path.join(wd, 'input.txt')
        output_file = os.path.join(wd, 'output.txt')

        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

    def _exists(self):
        if not self._expected_to_exist:
            exists = os.path.exists(self.path)
            if exists:
                self._expected_to_exist = True
                return True
            else:
                return False
        else:
            return True 

    def __repr__(self):
        if self._exists():
            return f"CONTUR Executable at {self.path}"
        else:
            return f"CONTUR Executable NOT FOUND (expected at {self.path})"
