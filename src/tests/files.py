import os
import re
import glob
from file import File
from zone_parser import ZoneParser

class Patterns:
    FILE_STATEMENT = re.compile(r'(file|file_debug|file_release):\s*([\~\-\&\w\/\.\*]+)\s+([\~\-\&\w\/\.\*]+)', re.MULTILINE)
    SERVERFILE_STATEMENT = re.compile(r'(serverfile|serverfile_debug|serverfile_release):\s*([\~\-\&\w\/\.\*]+)\s+([\~\-\&\w\/\.\*]+)', re.MULTILINE)

def _process(self: ZoneParser, test: re.Match[str]):
    if self.project is None: # Apenas para fazer a tipagem parar de reclamar.
        return

    file_type: str = test[1]
    file_source: str = test[2]
    file_dest: str = test[3]

    for search_path in self.project.asset_search_path:
        current_path = os.path.join(search_path, file_source)
        for path in glob.glob(current_path, recursive=True):
            relative_path = os.path.relpath(path, os.path.commonpath([current_path.rstrip("*/"), path]))
            dest_path = os.path.normpath(os.path.join(file_dest, relative_path))

            if file_type == 'file':
                file = self.project.get_file(dest_path)
                if file is not None:
                    from_source_mod = file.source.startswith(os.path.join(self.project.home, 'src'))
                    if from_source_mod:
                        continue

                    self.project.files.remove(file)

                self.project.files.append(File(path, dest_path))
                continue

            if file_type.startswith('file') and file_type.endswith(self.project.target):
                file = self.project.get_file(dest_path)
                if file is not None:
                    from_source_mod = file.source.startswith(os.path.join(self.project.home, 'src'))
                    if from_source_mod:
                        continue

                    self.project.files.remove(file)

                self.project.files.append(File(path, dest_path))
                continue

            if file_type == 'serverfile':
                file = self.project.get_serverfile(dest_path)
                if file is not None:
                    from_source_mod = file.source.startswith(os.path.join(self.project.home, 'src'))
                    if from_source_mod:
                        continue

                    self.project.serverfiles.remove(file)

                self.project.serverfiles.append(File(path, dest_path))
                continue

            if file_type.startswith('serverfile') and file_type.endswith(self.project.target):
                file = self.project.get_serverfile(dest_path)
                if file is not None:
                    from_source_mod = file.source.startswith(os.path.join(self.project.home, 'src'))
                    if from_source_mod:
                        continue

                    self.project.serverfiles.remove(file)

                self.project.serverfiles.append(File(path, dest_path))

def files(self: ZoneParser, line: str) -> bool:
    if self.project is None:
        raise Exception('no project found')
    
    test1 = re.match(Patterns.FILE_STATEMENT, line)
    test2 = re.match(Patterns.SERVERFILE_STATEMENT, line)
    if test1 is None and test2 is None:
        return False

    if test1 is not None:
        _process(self, test1)

    if test2 is not None:
        _process(self, test2)
    
    self.output.append(f'// {line}')
    return True