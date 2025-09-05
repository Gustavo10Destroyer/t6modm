import os
from i18n import _
from colors import Colors
from typing import Any, Dict, List, Callable
from project import Project
from exceptions import FileNotFoundException, ZoneNotFoundException

ENDLINE = '\n'

class ZoneParser:
    is_dependency = False

    def __init__(self, file_path: str):
        self.tests: List[Callable[['ZoneParser', str], bool]] = []
        self.output: List[str] = []
        self.project: Project | None = None
        self.scripts: List[str] = []
        self.source_path = file_path
        self.variables: Dict[str, Any] = {}

        self.dependency: bool = ZoneParser.is_dependency
        ZoneParser.is_dependency = True

    def parse(self) -> str:
        if not os.path.isfile(self.source_path):
            raise FileNotFoundException(self.source_path)

        self.output: List[str] = []
        with open(self.source_path, 'r') as source_file:
            source = source_file.read()

        for line in source.split(ENDLINE):
            prevent = False
            for test in self.tests:
                try:
                    prevent = test(self, line)
                except ZoneNotFoundException as err:
                    message = _("%s isn't a valid file!")
                    print(f'[{Colors.RED}ERR!{Colors.RESET}] {message % err}')

                if prevent: break

            if not prevent:
                self.output.append(line)

        return ENDLINE.join(self.output)