from zone_parser import ZoneParser

def filter_headers(self: ZoneParser, line: str) -> bool:
    if line.strip().startswith('>name,') or line.strip().startswith('>game,'):
        self.output.append(f'// {line}')
        return True

    return False