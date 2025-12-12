# -*- coding: utf-8 -*-

import sys
sys.dont_write_bytecode = True

import os
import json
import shutil
import subprocess

from i18n import _
from uuid import uuid4 as uuid
from setup import setup_tool, remove_tool
from colors import Colors
from update import update_tool
from project import Project
from zipfile import ZipFile
from exceptions import FileNotFoundException
from zone_parser import ZoneParser
from argument_parser import argument_parser
from tests.files import files
from tests.filter_gsc import filter_gsc
from tests.include_zone import include_zone
from tests.filter_headers import filter_headers
from tests.ignore_comments import ignore_comments

def build_project(project: Project):
    if os.environ.get('OAT_HOME') is None:
        message = _('The environment variable %s is not defined. You can define on a .t6modm.env file!')
        print(f'[{Colors.RED}ERR!{Colors.RESET}] {message % 'OAT_HOME'}')
        sys.exit(1)

    if os.environ.get('GAME_HOME') is None:
        message = _('The environment variable %s is not defined. You can define on a .t6modm.env file!')
        print(f'[{Colors.RED}ERR!{Colors.RESET}] {message % 'GAME_HOME'}')
        sys.exit(1)

    source_path = os.path.join(project.home, 'src', 'zone_source', 'mod.zone')
    if not os.path.isfile(source_path):
        message = _('The file %s does not exist.')
        print(f'[{Colors.RED}ERR!{Colors.RESET}] {message % source_path}')
        sys.exit(1)

    shutil.rmtree(os.path.join(project.home, 'src', 'zone_source', 'tempzones'), ignore_errors=True)

    parser = ZoneParser(source_path)
    parser.project = project

    # Abaixo estão os testes que serão executados para cada linha
    # A ordem dos fatores importa!
    parser.tests.append(ignore_comments) # 1
    parser.tests.append(filter_headers)  # 2
    parser.tests.append(filter_gsc)      # 3
    parser.tests.append(include_zone)    # 4
    parser.tests.append(files)           # 5

    args = argument_parser.parse_args()
    output_folder: str = args.output_folder if args.output_folder is not None else os.path.join(project.home, 'compiled')

    output_path = os.path.join(project.home, 'src', 'zone_source', 'tempzones', 'mod.zone')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as output_file:
        output_file.write('>game,T6\n')
        output_file.write('>name,mod\n')
        output_file.write(parser.parse())

        for dependency in project.dependencies:
            dependency_path = dependency.replace('$HOME', project.home)
            dependency_zone_path = os.path.join(dependency_path, 'src', 'zone_source', 'mod.zone')
            if os.path.isfile(dependency_zone_path):
                dependency_parser = ZoneParser(dependency_zone_path)
                dependency_parser.project = project

                dependency_parser.tests = parser.tests.copy()
                output_file.write('\n// Dependency: ' + os.path.basename(dependency) + '\n')

                dependency_temp_name = str(uuid())
                with open(os.path.join(project.home, 'src', 'zone_source', 'tempzones', f'{dependency_temp_name}.zone'), 'w') as dependency_temp_file:
                    dependency_temp_file.write(dependency_parser.parse())

                output_file.write(f'include,tempzones/{dependency_temp_name}\n')

    if args.wait:
        code_path = shutil.which('code')
        if code_path:
            code = subprocess.Popen([code_path, '--wait', output_path])
            code.wait()

        if code_path is None:
            notepad_path = shutil.which('notepad')
            if notepad_path is None:
                message = _('Failed to locate VSCode and Notepad on your system.')
                print(f'[{Colors.RED}ERR!{Colors.RESET}] {message}')
                sys.exit(1)

            notepad = subprocess.Popen([notepad_path, output_path])
            notepad.wait()

    if len(project.filtered_scripts) == 0:
        message = _('No scripts filtered.')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message}')
    else:
        message = _('%(amount)s %(noun)s filtered.')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message % {'amount': len(project.filtered_scripts), 'noun': 'script' if len(project.filtered_scripts) < 2 else 'scripts'}}')

    shutil.rmtree(output_folder, ignore_errors=True) # Limpar o diretório de saída
    # ! IMPORTANTE: O diretório de saída deve existir antes de chamar o Linker (ele cria automaticamente se não existir, mas existe um bug com soundbanks caso não exista, a compilação funciona, mas o OAT diz que falhou)
    os.makedirs(output_folder, exist_ok=True)

    oat_binary = 'Linker.exe' if os.name == 'nt' else 'Linker'

    command = [
        os.path.join(os.environ.get('OAT_HOME', ''), oat_binary),
        '-v',
        '--output-folder', output_folder,
        '--base-folder', os.environ.get('OAT_HOME', ''),
        '--source-search-path', os.path.join(project.home, 'src', 'zone_source'),
        '--add-asset-search-path', os.path.join(project.home, 'src'),
        '--add-asset-search-path', os.path.join(os.environ.get('GAME_HOME', ''), 'zone', 'all'),
        '--add-asset-search-path', os.path.join(os.environ.get('GAME_HOME', ''), 'zone', 'english'),
    ]

    for fastfile in project.fastfiles:
        command.append('--load')
        command.append(fastfile.replace('$GAME_HOME', os.environ.get('GAME_HOME', '')).replace('$HOME', project.home))

    for dependency in project.dependencies:
        dependency_home = dependency.replace('$HOME', project.home)
        command.append('--add-asset-search-path')
        command.append(os.path.join(dependency_home, 'src'))

    command.append(f'tempzones\\mod')

    message = _('Building the project for target %s...')
    print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message % project.target}')

    # For debug purposes only
    # print(f'OAT_HOME={os.environ.get("OAT_HOME", "")}')
    # print(f'GAME_HOME={os.environ.get("GAME_HOME", "")}')
    # print('\n'.join(command))
    # return

    oat = subprocess.Popen(command, shell=True, text=True)
    oat.wait()

    if oat.returncode != 0:
        message = _('Build failed!')
        print(f'[{Colors.RED}ERR!{Colors.RESET}] {message}')
        sys.exit(1)

    message = _('Build completed successfully!')
    print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message}')

    if len(project.files) > 0:
        with ZipFile(os.path.join(output_folder, 'mod.iwd'), 'w') as zipfile:
            for file in project.files:
                # print(f'{file.source} -> {file.dest}')
                zipfile.write(file.source, file.dest)

        message = _('Created %s')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message % 'mod.iwd'}')

    if len(project.serverfiles) > 0 or len(project.filtered_scripts) > 0:
        with ZipFile(os.path.join(output_folder, 'server-only.zip'), 'w') as zipfile:
            for file in project.serverfiles:
                # print(f'{file.source} -> {file.dest}')
                zipfile.write(file.source, file.dest)

            for script in project.filtered_scripts:
                zipfile.write(script.source, script.dest)

        message = _('Created %s')
        print(f'[{Colors.GREEN}INFO{Colors.RESET}] {message % 'server-only.zip'}')

    with open(os.path.join(output_folder, 'mod.json'), 'w') as manifest_file:
        json.dump({
            'name': project.name,
            'description': project.description,
            'version': project.version,
            'author': project.author
        }, manifest_file, indent=4, ensure_ascii=False)

def main():
    global current_project

    args = argument_parser.parse_args()
    if args.action == 'build':
        project_dir = args.project_dir
        file_path = os.path.join(project_dir, 'project.t6modm.json')

        try:
            project = Project.from_file(file_path)
        except FileNotFoundException:
            message = _('That is not a project!')
            print(f'[{Colors.RED}ERR!{Colors.RESET}] {message}')
            sys.exit(1)

        project.target = args.target
        build_project(project)
        return

    if args.action == 'setup':
        if args.remove == True:
            remove_tool()
            return

        setup_tool()
        return
    
    if args.action == 'update':
        update_tool()

if __name__ == '__main__':
    main()