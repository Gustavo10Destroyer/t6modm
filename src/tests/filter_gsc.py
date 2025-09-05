import os
import re
from i18n import _
from file import File
from colors import Colors
from zone_parser import ZoneParser

class Patterns:
    NOIGNORE = re.compile(r'\/\/\s*noignore', re.MULTILINE)
    SCRIPT_STATEMENT = re.compile(r'script,\s*([^ ]+?)(?=\s*\/\/|$)', re.MULTILINE)

def filter_gsc(self: ZoneParser, line: str) -> bool:
    if self.project is None:
        raise Exception('no project found')

    if self.project.target == 'debug':
        return False

    test = re.match(Patterns.SCRIPT_STATEMENT, line)
    if test is None:
        return False

    original_path: str = test[1]
    if not original_path.endswith('.gsc'):
        return False

    abs_file_path: str = os.path.join(self.project.home, 'src', original_path)

    exists: bool = False
    for search_path in self.project.asset_search_path:
        abs_file_path = os.path.join(search_path, os.path.normpath(original_path))
        if os.path.isfile(abs_file_path):
            exists = True
            break

    if not exists:
        message = _('The script %(prefix)s%(content)s%(suffix)s cannot be ignored, as it is imported from another fastfile. This may cause problems!')
        print(f'[{Colors.YELLOW}WARN{Colors.RESET}] {message % {'prefix': Colors.DARK_GRAY, 'content': f'{original_path.replace(os.path.basename(original_path), f'{Colors.YELLOW}{os.path.basename(original_path)}')}', 'suffix': Colors.RESET}}')
        print(f'↳   {self.source_path}:{len(self.output)+1}')
        return False

    noignore = re.findall(Patterns.NOIGNORE, line)
    if len(noignore) == 0:
        print(f'[DEBUG] Ignored script: {original_path}')
        self.project.filtered_scripts.append(File(abs_file_path, original_path))
        self.output.append(f'// {line}')
        return True

    message = _('The %(prefix)s%(content)s%(suffix)s script isn\'t being ignored. This may cause problems!')
    print(f'[{Colors.YELLOW}WARN{Colors.RESET}] {message % {'prefix': Colors.DARK_GRAY, 'content': f'{original_path.replace(os.path.basename(original_path), f'{Colors.YELLOW}{os.path.basename(original_path)}')}', 'suffix': Colors.RESET}}')
    return False