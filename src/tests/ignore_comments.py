from zone_parser import ZoneParser

def ignore_comments(self: ZoneParser, line: str) -> bool:
    return line.strip().startswith('//')