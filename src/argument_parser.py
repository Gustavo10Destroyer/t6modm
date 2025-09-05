__version__ = '1.0.0b'

import os
import argparse
from i18n import _

argument_parser = argparse.ArgumentParser('t6modm', description=_('A tool for creating and managing modding projects for Call of Duty: Black Ops 2'))
argument_parser.add_argument('--version', action='version', version=f'T6MODM v{__version__}')
subparsers = argument_parser.add_subparsers(title='command', dest='action', required=True)

build_parser = subparsers.add_parser('build', help=_('Build the project'))
build_parser.add_argument('--wait', action='store_true', default=False, help=_('Wait for manual review of the generated zonefile'))
build_parser.add_argument('--target', choices=['debug', 'release'], default='debug', help=_('Build target'))
build_parser.add_argument('--project-dir', default=os.getcwd(), help=_('The directory where the project is located'))
build_parser.add_argument('--output-folder', help=_('The output directory'))

setup_parser = subparsers.add_parser('setup', help=_('Setup the tool into your environment'))
setup_parser.add_argument('--remove', action='store_true', default=os.getcwd(), help=_('Remove the tool from your environment'))

update_parser = subparsers.add_parser('update', help=_('Update the tool'))