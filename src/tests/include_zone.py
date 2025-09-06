import os
import re
from i18n import _
from uuid import uuid4 as uuid
from colors import Colors
from exceptions import ZoneNotFoundException
from zone_parser import ZoneParser

class Patterns:
    INCLUDE = re.compile(r'include,\s*([^ ]+?)(?=\s*\/\/|$)')

def include_zone(self: ZoneParser, line: str) -> bool:
    if self.project is None:
        raise Exception('no project found.')

    test = re.match(Patterns.INCLUDE, line)
    if test is None:
        return False

    search_path = None
    zone_path: str = ''
    for search_path in self.project.asset_search_path:
        zone_path: str = os.path.join(search_path, 'zone_source', test[1])
        if not os.path.isfile(f'{zone_path}.zone'):
            search_path = None
            continue

        break

    if search_path is None:
        raise ZoneNotFoundException(self.source_path, f'{zone_path}.zone')

    zone_parser = ZoneParser(f'{zone_path}.zone')
    zone_parser.project = self.project
    zone_parser.tests = self.tests.copy()

    temp_zone_name = str(uuid())
    temp_zone_path = os.path.join(self.project.home, 'src', 'zone_source', 'tempzones', temp_zone_name)

    os.makedirs(os.path.dirname(temp_zone_path), exist_ok=True)

    with open(f'{temp_zone_path}.zone', 'w') as zone_file:
        try:
            zone_file.write(zone_parser.parse())
        except ZoneNotFoundException as err:
            message = _('The file %(prefix)s"%(content)s"%(sufix)s doesn\'t exist!')
            print(f'[{Colors.RED}ERR!{Colors.RESET}] {message % {'prefix':Colors.YELLOW, 'content':err.file_path, 'sufix':Colors.RESET}}')
            raise

    self.output.append(f'include,{temp_zone_path} // {line}')
    return True