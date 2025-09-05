import os
import sys
import subprocess
from i18n import _
from colors import Colors

def update_tool():
    git = subprocess.Popen(['git', 'pull'], cwd=os.path.dirname(sys.argv[0]), shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = git.communicate()

    if stdout.startswith('Already up to date.'):
        message = _('The tool is already up to date.')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message}')
        return

    if git.returncode == 0:
        message = _('The tool has been updated.')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message}')
        return

    message = _('An error occurred while trying to update the tool')
    sys.stderr.write(f'[{Colors.RED}ERR!{Colors.RESET}] {message}: {stderr}\n')
    sys.exit(git.returncode)