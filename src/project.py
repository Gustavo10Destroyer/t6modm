import os
import json
from file import File
from dotenv import load_dotenv
from typing import List
from exceptions import FileNotFoundException

class Project:
    def __init__(
        self,
        home: str,
        name: str,
        description: str,
        version: str,
        author: str,
        fastfiles: List[str],
        dependencies: List[str]
    ):
        load_dotenv(os.path.join(home, '.t6modm.env'))

        self.home = home
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.fastfiles = fastfiles
        self.dependencies = dependencies
        self.target: str = 'debug'
        self.files: List[File] = [] # Arquivos que vão para o IWD
        self.serverfiles: List[File] = [] # Arquivos que vão para o mod.
        self.filtered_scripts: List[File] = []
        self.asset_search_path: List[str] = [os.path.join(home, 'src')]

        for dependency in dependencies:
            self.asset_search_path.append(os.path.join(dependency.replace('$HOME', home), 'src'))

    def to_file(self, file_path: str) -> None:
        dirname = os.path.dirname(file_path)
        if len(dirname) > 0:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            json.dump({
                'name': self.name,
                'description': self.description,
                'version': self.version,
                'author': self.author,
                'fastfiles': self.fastfiles,
                'dependencies': self.dependencies,
            }, file, indent=4)

    @classmethod
    def from_file(cls, file_path: str):
        if not os.path.isfile(file_path):
            raise FileNotFoundException(file_path)

        with open(file_path, 'r') as file:
            data = json.load(file)

        name: str = data.get('name', '')
        description: str = data.get('description', '')
        version: str = data.get('version', '')
        author: str = data.get('author', '')
        fastfiles: List[str] = data.get('fastfiles', [])
        dependencies: List[str] = data.get('dependencies', [])
        return cls(os.path.dirname(file_path), name, description, version, author, fastfiles, dependencies)

    def get_file(self, dest_path: str) -> File | None:
        for file in self.files:
            if file.dest == dest_path:
                return file

    def get_serverfile(self, dest_path: str) -> File | None:
        for file in self.serverfiles:
            if file.dest == dest_path:
                return file