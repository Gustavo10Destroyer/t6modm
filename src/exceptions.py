class FileNotFoundException(Exception):
    def __init__(self, file_path: str):
        Exception.__init__(self, f'"{file_path}" isn\'t a valid file')
        self.file_path = file_path

class ZoneNotFoundException(Exception):
    def __init__(self, source: str, file_path: str):
        Exception.__init__(self, f'"{file_path}" isn\'t a valid file, at {source}')
        self.source = source
        self.file_path = file_path