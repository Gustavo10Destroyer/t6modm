import os
import sys
from i18n import _
from colors import Colors

def setup_tool():
    file_path = os.path.expandvars(r'$localappdata\Microsoft\WindowsApps\t6modm.cmd')
    if os.path.isfile(file_path):
        message = _('The tool is already in your environment, use %s for help.')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message % f'{Colors.YELLOW}t6modm --help{Colors.RESET}'}')
        return

    with open(file_path, 'wb') as file:
        file.write(f'@echo off\nchcp 65001 >nul\n"{sys.executable}" "{os.path.normpath(os.path.abspath(sys.argv[0]))}" %*'.encode('utf-8'))

    message = _('The tool has been added to your environment.')
    print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message}')

def remove_tool():
    file_path = os.path.expandvars(r'$localappdata\Microsoft\WindowsApps\t6modm.cmd')
    if not os.path.isfile(file_path):
        message = _('The tool is not installed.')
        print(f'[{Colors.RED}ERR!{Colors.RESET}] {message}')
        sys.exit(1)

    os.unlink(file_path)
    message = _('The tool has been removed from your environment.')
    print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message}')