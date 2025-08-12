import os
import re
import sys
import glob
import json
import uuid
import shutil
import zipfile
import argparse
import requests
import subprocess

from typing import Any, Dict, List, Tuple

RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
RESET = '\x1b[0m'
CYAN = '\x1b[36m'
DEBUG_HEADER = '\x1b[35mDEBUG\x1b[0m'

def create_project(args: argparse.Namespace) -> None:
    oat: str = args.oat
    name: str = args.name
    game_dir: str = args.game_dir
    directory: str | None = args.directory
    description: str = args.description

    variables = load_vars(os.path.expanduser(r'~/.t6modm.vars.json'))
    game_dir = parse_variables(game_dir, variables)
    if len(game_dir) > 0 and not os.path.isdir(game_dir):
        print(f'[{YELLOW}WARN{RESET}] O diretório do jogo não foi encontrado!')

    if directory is None:
        directory = os.path.join(os.getcwd(), name)

    directory = os.path.abspath(directory)

    if os.path.exists(directory) and len(os.listdir(directory)) > 0:
        sys.stderr.write(f'[{RED}ERR!{RESET}] A pasta {YELLOW}"{directory}"{RESET} já existe e não está vazia!\r\n')
        sys.exit(1)

    print(f'Nome do projeto: {name}')
    print(f'Diretório do projeto: {directory}')
    print(f'Descrição do projeto: {description}')

    os.makedirs(os.path.join(directory, 'src'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'src', 'images'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'src', 'scripts'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'src', 'zone_source'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'src', 'english', 'localizedstrings'), exist_ok=True)

    print(f'[{YELLOW}INFO{RESET}] Buscando pela versão do OAT {oat}...')
    if oat == 'latest':
        url = f'https://api.github.com/repos/Laupetin/OpenAssetTools/releases/latest'
    else:
        if not oat.startswith('v'):
            oat = 'v' + oat
        url = f'https://api.github.com/repos/Laupetin/OpenAssetTools/releases/tags/{oat}'

    res = requests.get(url)

    try:
        res.raise_for_status()
    except requests.HTTPError as e:
        print(e)
        raise

    print(f'[{GREEN}INFO{RESET}] Versão encontrada!')

    release = res.json()
    for asset in release.get('assets', []):
        if asset['name'] == 'oat-windows.zip':
            break

    download_url: str = asset['browser_download_url'] # type: ignore
    print(f'[{YELLOW}INFO{RESET}] Baixando OAT {oat} ({download_url})...')
    file_res = requests.get(download_url) # type: ignore
    file_res.raise_for_status()

    oat_zip_path = os.path.join(directory, asset.get('name', 'oat-windows.zip'))# type: ignore
    with open(oat_zip_path, 'wb') as f:
        f.write(file_res.content)

    oat_path = os.path.join(directory, 'oat', oat)
    with zipfile.ZipFile(oat_zip_path) as zip:
        zip.extractall(oat_path)
    os.unlink(oat_zip_path)
    print(f'[{GREEN}INFO{RESET}] O OAT foi baixado em {oat_path}.')

    details = {
        'oat': oat_path,
        'name': name,
        'author': '',
        'version': '1.0.0',
        'game_dir': game_dir,
        'repository':'',
        'description': description,
    }

    with open(os.path.join(directory, 'project.t6modm.json'), 'w') as file:
        json.dump(details, file, indent=4)

    with open(os.path.join(directory, 'src', 'english', 'localizedstrings', 'mod.str'), 'w') as file:
        file.write('VERSION             "1"\nCONFIG              ""\nFILENOTES           ""\n\nREFERENCE           MESSAGE_T6MODM\nLANG_ENGLISH        "Feito com T6MODM"\n\nENDMARKER')

    with open(os.path.join(directory, 'src', 'zone_source', 'mod.zone'), 'w') as file:
        file.write('>game,T6\n\nlocalize,mod')

def load_vars(file_path: str) -> Dict[str, str | Any]:
    if not os.path.isfile(file_path):
        print(f'[{DEBUG_HEADER}] O arquivo {YELLOW}{file_path}{RESET} não existe.')
        return {}

    with open(file_path, 'r') as file:
        return json.load(file)

def parse_variables(data: Any, variables: Dict[str, str | Any]) -> Any:
    if isinstance(data, str):
        def sub(m: re.Match[str]) -> str:
            v = variables.get(m[1], '')
            if v is None:
                print(f'[{YELLOW}WARN{RESET}] A variável {m[1]} não está definida mas é usada pelo projeto.')
            return v
        return re.sub(r'{{VAR:([$\w\.]+)}}', sub, data) # type: ignore

    if isinstance(data, dict):
        for key, value in data.items(): # type: ignore
            data[key] = parse_variables(value, variables)

        return data # type: ignore

    if isinstance(data, list):
        for index, item in enumerate(data): # type: ignore
            data[index] = parse_variables(item, variables)

    return data # type: ignore

def load_project(project_dir: str) -> Dict[str, Any]:
    project = os.path.join(project_dir, 'project.t6modm.json')

    if not os.path.isfile(project):
        raise Exception('invalid project')

    global_variables = load_vars(os.path.expanduser('~/.t6modm.vars.json'))
    extras = {
        '$home': project_dir
    }

    variables: Dict[str, str | Any] = {**global_variables, **load_vars(os.path.join(project_dir, '.t6modm.vars.json')), **extras}

    with open(project, 'r') as file:
        data: Dict[str, Any] = json.load(file)
        data['game_dir'] = parse_variables(data.get('game_dir', ''), variables)
        game_dir: str = data.get('game_dir', '')
        variables['$game_dir'] = game_dir
        data = parse_variables(data, variables) # type: ignore

    return data

def install_dependency(args: argparse.Namespace) -> None:
    raise NotImplementedError
    static: bool = args.static # type: ignore
    dependency_type: str = args.type
    dependency_origin: str = args.origin # type: ignore


    if dependency_type == 'fastfile':
        try:
            project = load_project(os.getcwd())
        except Exception:
            sys.stderr.write(f'[{RED}ERR!{RESET}] Ocorreu um erro ao tentar abrir o arquivo {YELLOW}project.t6modm.json{RESET}. Você está na pasta de um projeto?')
            sys.exit(1)

        print(project)

def config(args: argparse.Namespace) -> None:
    home: str = os.getcwd() if args.home is None else args.home
    is_global: bool = args.g
    unset: bool = args.unset
    name: str = args.name
    value: str | None = args.value

    noun = 'GLOBAL' if is_global else 'LOCAL'
    file_path = os.path.expanduser('~/.t6modm.vars.json') if is_global else os.path.join(home, '.t6modm.vars.json')
    if unset and not os.path.isfile(file_path):
        print(f'[{GREEN}INFO{RESET}] [{noun}] A variável {name} não está configurada.')
        return

    if value is None and not unset:
        if not os.path.isfile(file_path):
            print(f'[{GREEN}INFO{RESET}] [{noun}] A variável {name} não está configurada.')
            return

        with open(file_path, 'r') as file:
            data = json.load(file)
            value = data.get(name)
            if value is None:
                print(f'[{GREEN}INFO{RESET}] [{noun}] A variável {YELLOW}{name}{RESET} não está configurada.')
                return

            print(f'[{GREEN}INFO{RESET}] [{noun}] {name}: {value}')

        return

    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)

    if unset:
        with open(file_path, 'r') as file:
            variables = json.load(file)
            if variables.get(name) is None:
                print(f'[{GREEN}INFO{RESET}] [{noun}] A variável {YELLOW}{name}{RESET} não está configurada.')
                return

            file.close()
            del variables[name]

            if len(variables.keys()) == 0:
                os.unlink(file_path)
            else:
                with open(file_path, 'w') as file:
                    json.dump(variables, file, indent=True, ensure_ascii=False)

            print(f'[{GREEN}INFO{RESET}] [{noun}] A variável {YELLOW}{name}{RESET} foi apagada.')
            return

    variables = {}
    variables[name] = value

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            variables = json.load(file)
            variables[name] = value

    with open(file_path, 'w') as file:
        json.dump(variables, file, indent=4, ensure_ascii=False)

    print(f'[{GREEN}INFO{RESET}] [{noun}] A variável {YELLOW}{name}{RESET} foi definida como: {YELLOW}{value}{RESET}.')

def build_project(args: argparse.Namespace) -> None:
    y: bool | None = args.y
    mode: str = args.mode
    quiet: bool = args.quiet
    project_home = args.home if args.home is not None else os.getcwd()

    if not quiet:
        print(f'[{CYAN}INFO{RESET}] Diretório do projeto: {project_home}')

    try:
        project = load_project(project_home)
    except Exception as err:
        print(f'[{RED}ERR!{RESET}] Falha ao tentar compilar: {RED}{err}{RESET}.\n  Você está num projeto?')
        sys.exit(1)

    oat: str | None = project.get('oat')
    project_name: str | None = project.get('name')
    # print(project)

    if oat is None:
        sys.stderr.write(f'[{RED}ERR!{RESET}] Ocorreu um erro ao tentar compilar o projeto, parece que seu OAT não está definido.\r\n')
        sys.exit(1)
 
    if project_name is None:
        sys.stderr.write(f'[{RED}ERR!{RESET}] Ocorreu um erro ao tentar compilar o projeto, o projeto não tem nome.\r\n')
        sys.exit(1)

    game_dir: str | None = project.get('game_dir')
    if game_dir is None:
        sys.stderr.write(f'[{RED}ERR!{RESET}] Ocorreu um erro ao tentar compilar o projeto, parece que o diretório do jogo não foi configurado!\r\n')
        sys.exit(1)

    linker = os.path.join(oat, 'Linker.exe')
    print(linker)
    command = [
        linker,
        '-v',
        '--base-folder',
        oat,
        '--add-asset-search-path',
        os.path.join(project_home, 'src'),
        '--add-asset-search-path',
        os.path.join(game_dir, 'zone', 'all'),
        '--add-asset-search-path',
        os.path.join(game_dir, 'zone', 'english'),
        '--source-search-path',
        os.path.join(project_home, 'src', 'zone_source'),
    ]

    source_path: List[str] = [project_home]
    dependencies: List[Dict[str, str]] = project.get('dependencies', [])
    for dependency in dependencies:
        if dependency['type'] == 'fastfile':
            command.append('--load')
            command.append(dependency['origin'])

        if dependency['type'] == 'project':
            build_args = argparse.Namespace()
            build_args.y = None
            build_args.dest = None
            build_args.mode = mode
            build_args.wait = False
            build_args.quiet = True
            build_args.home = dependency['origin']

            proj = load_project(dependency['origin'])
            build_project(build_args)
            name = proj.get('name')

            if not quiet:
                print(f'[{GREEN}INFO{RESET}] A dependência {YELLOW}{name}{RESET} foi compilada com sucesso.')

            fastfile_path = os.path.join(dependency['origin'], 'compiled', 'mod.ff')
            command.append('--add-asset-search-path')
            command.append(os.path.join(dependency['origin'], 'src'))
            source_path.append(dependency['origin'])

            command.append('--load')
            command.append(fastfile_path)

    command.append('--output-folder')
    command.append(os.path.join(project_home, 'compiled'))

    zone_path = os.path.join(project_home, 'src', 'zone_source', 'mod.zone')
    if not os.path.isfile(zone_path):
        sys.stderr.write(f'[{RED}ERR!{RESET}] Ocorreu um erro ao tentar compilar o projeto. O arquivo {YELLOW}src/zone_source/mod.zone{RESET} não foi encontrado.\r\n')
        sys.exit(1)

    mod_files: List[Tuple[str, str]] = []    # Carregado no IWD
    server_files: List[Tuple[str, str]] = [] # Um zip separado que NÃO deve ser enviado ao jogador
    scripts: List[str] = []
    def parse_lines(lines: List[str]) -> List[str]:
        nonlocal mod_files
        nonlocal scripts

        for line in list(lines):
            if line.strip().startswith('//'):
                continue

            if line.strip().startswith('>name,') or line.strip().startswith('>game,'):
                lines.remove(line)

            if mode == 'release' and line.strip().startswith('script,'):
                if line.strip().endswith('noignore'):
                    if not quiet:
                        print(f'[{RED}WARN{RESET}] Um script não está sendo ignorado no modo release. Isso pode ser perigoso!')
                        print(f'  {line}')
                    continue

                if line.strip().endswith('.gsc'):
                    scripts.append(line.strip()[7:])
                    lines.remove(line)

            if line.strip().startswith('include,'):
                _, zone_name = line.strip().split(',', 1)
                zone_path = os.path.join(project_home, 'src', 'zone_source', f'{zone_name}.zone')

                if not os.path.isfile(zone_path):
                    sys.stderr.write(f'[{RED}ERR!{RESET}] Ocorreu um erro ao tentar compilar o projeto. O arquivo {YELLOW}{os.path.relpath(zone_path)}{RESET} não foi encontrado.\r\n')
                    sys.exit(1)

                lines.remove(line)
                with open(zone_path, 'r') as zone:
                    lines.append('\n')
                    lines += parse_lines(zone.readlines())

            test = re.match(r'(serverfile|serverfile_debug|serverfile_release):\s*([\w\/\.\*]+)\s+([\w\/\.]+)', line)
            if test is not None:
                lines.remove(line)

                file_mode: str = test[1]
                file_source: str = test[2]
                file_dest: str = test[3]
                if file_mode == 'serverfile':
                    server_files.append((file_source, file_dest))
                elif file_mode == 'serverfile_debug' and mode == 'debug':
                    server_files.append((file_source, file_dest))
                elif file_mode == 'serverfile_release' and mode == 'release':
                    server_files.append((file_source, file_dest))
                continue

            test = re.match(r'(file|file_debug|file_release):\s*([\w\/\.\*]+)\s+([\w\/\.]+)', line)
            if test is None:
                continue

            lines.remove(line)

            file_mode: str = test[1]
            file_source: str = test[2]
            file_dest: str = test[3]

            if file_mode == 'file':
                mod_files.append((file_source, file_dest))
            elif file_mode == 'file_debug' and mode == 'debug':
                mod_files.append((file_source, file_dest))
            elif file_mode == 'file_release' and mode == 'release':
                mod_files.append((file_source, file_dest))

        return lines

    file = open(zone_path, 'r')
    lines = parse_lines(file.readlines())
    file.close()

    temp_zone_name = f'{mode}_{str(uuid.uuid4())}'
    temp_zone_path = os.path.join(project_home, 'src', 'zone_source', f'{temp_zone_name}.zone')

    with open(temp_zone_path, 'w') as file:
        file.write('>game,T6\n')
        file.write('>name,mod\n')
        file.writelines(lines)

    command.append(temp_zone_name)

    if args.wait:
        p = subprocess.Popen(['code', '--wait', temp_zone_path], shell=True)
        p.wait()

    if not quiet:
        print(f'[{YELLOW}INFO{RESET}] Compilando no modo {mode}...')

    output_path = os.path.join(os.path.join(project_home, 'compiled'))
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    process = subprocess.Popen(command, shell=True)
    process.wait()
    if process.returncode != 0:
        sys.stderr.write(f'[{RED}ERR!{RESET}] Falha na compilação, código de saída: {process.returncode}\r\n')
        os.unlink(temp_zone_path)
        sys.exit(1)

    if len(mod_files) > 0:
        with zipfile.ZipFile(os.path.join(project_home, 'compiled', 'mod.iwd'), 'w') as file:
            for file_source, file_dest in mod_files:
                src = os.path.join(project_home, file_source)
                items = glob.glob(src, recursive=True)

                if not items:
                    sys.stderr.write(f'[{RED}ERR!{RESET}] Ao gerar o IWD: nenhum arquivo encontrado para {YELLOW}{file_source}{RESET}\r\n')
                    os.unlink(temp_zone_path)
                    sys.exit(1)

                if not file_dest.endswith('/') and not file_dest.endswith('\\'):
                    for item in items:
                        file.write(item, file_dest)
                    continue

                for item in items:
                    rel = os.path.relpath(item, os.path.commonpath([src.rstrip("*/"), item]))
                    destino_item = os.path.join(file_dest, rel)
                    file.write(item, destino_item)

    if len(server_files) > 0:
        with zipfile.ZipFile(os.path.join(project_home, 'compiled', 'server-only.zip'), 'w') as file:
            for file_source, file_dest in server_files:
                src = os.path.join(project_home, file_source)
                items = glob.glob(src, recursive=True)

                if not items:
                    sys.stderr.write(f'[{RED}ERR!{RESET}] Ao gerar o IWD: nenhum arquivo encontrado para {YELLOW}{file_source}{RESET}\r\n')
                    os.unlink(temp_zone_path)
                    sys.exit(1)

                if not file_dest.endswith('/') and not file_dest.endswith('\\'):
                    for item in items:
                        file.write(item, file_dest)
                    continue

                for item in items:
                    rel = os.path.relpath(item, os.path.commonpath([src.rstrip("*/"), item]))
                    destino_item = os.path.join(file_dest, rel)
                    file.write(item, destino_item)

    with open(os.path.join(output_path, 'mod.json'), 'w') as file:
        project_desc: str = project.get('description', 'No description provided')
        project_author: str = project.get('author', 'Unknown')
        project_version: str = project.get('version', 'Unknown')

        json.dump({
            'name': project_name,
            'description': project_desc,
            'author': project_author,
            'version': project_version
        }, file, indent=4, ensure_ascii=False)

    os.unlink(temp_zone_path)
    if not quiet:
        print(f'[{GREEN}INFO{RESET}] Compilado com sucesso.')
        print(f'[{CYAN}INFO{RESET}] Lista de scripts ignorados do fastfile: {scripts}')
        print(f'[{CYAN}INFO{RESET}] Lista de arquivos incluídos no IWD: {list(map(lambda files: os.path.relpath(files[0]), mod_files))}')
        print(f'[{CYAN}INFO{RESET}] Lista de arquivos server-side only: {list(map(lambda files: os.path.relpath(files[0]), server_files))}')

    dest: str | None = args.dest
    if dest is None:
        return

    if os.path.isfile(dest):
        print(f'[{YELLOW}WARN{RESET}] Não foi possível copiar o resultado para o destino. O caminho especificado aponta para um arquivo!')
        return

    if os.path.isdir(dest) and len(os.listdir(dest)) > 0 and not y:
        print(f'[{YELLOW}WARN{RESET}] O diretório de destino já existe e não está vazio! (Use -y para ignorar. OBS: Isso ira apagar todo o conteúdo do destino!)')
        return

    if os.path.isdir(dest):
        for item in os.listdir(dest):
            path = os.path.join(dest, item)
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    os.makedirs(dest, exist_ok=True)

    for item in os.listdir(output_path):
        shutil.copy(os.path.join(output_path, item), os.path.join(dest, item))

    if not quiet:
        print(f'[{GREEN}INFO{RESET}] O resultado foi movido para {YELLOW}"{dest}"{RESET}.')

def main() -> None:
    parser = argparse.ArgumentParser(description='Uma ferramenta para criar e gerenciar projetos de modding para Call of Duty: Black Ops 2')
    subparsers = parser.add_subparsers(dest='action', required=True)

    # Sub-comando: create
    create_parser = subparsers.add_parser('create', help='Cria um novo projeto')
    create_parser.add_argument('name', help='Nome do projeto')
    create_parser.add_argument('game_dir', nargs='?', default='{{VAR:GAME_DIR}}', help='Caminho para o diretório do jogo')
    create_parser.add_argument('--oat', help='Versão do OAT que será usada (padrão: latest)', default='latest')
    create_parser.add_argument('--directory', help='Diretório onde o projeto será criado', default=None)
    create_parser.add_argument('--description', help='Descrição do projeto', default='Projeto criado com t6modm')

    # Sub-comando: install
    install_parser = subparsers.add_parser('install', help='Instala uma dependência no projeto. A dependência precisa ser um projeto criado com esta ferramenta')
    install_parser.add_argument('type', choices=['project', 'fastfile'], help='Tipo de dependência: fastfile, project')
    install_parser.add_argument('origin', help='Caminho da dependência, também pode ser uma URL de um repositório git remoto')
    install_parser.add_argument('--static', action='store_true', help='Salva a dependência na pasta do projeto')

    # Sub-comando: build
    build_parser = subparsers.add_parser('build', help='Constrói o projeto atual.')
    build_parser.add_argument('--home', help='O diretório principal do projeto (pasta atual, por padrão).')
    build_parser.add_argument('--mode', choices=['debug', 'release'], default='debug', help='Tipo de compilação. Em debug, tudo é embalado no mod, em release, os scripts GSC e tudo mais que não precisa estar no mod é separado.')
    build_parser.add_argument('--dest', help='Após a compilação bem-sucedida, o resultado será movido para este destino.')
    build_parser.add_argument('--wait', action='store_true', help='Esta flag faz a compilação esperar que você revise o zone de compilação manualmente antes de proseguir.')
    build_parser.add_argument('--quiet', action='store_true', default=False, help='Esta flag compila o código com o mínimo de logs possível.')
    build_parser.add_argument('-y', action='store_true', help='Limpar o diretório de destino, caso já exista.')

    # Sub-comando: config
    config_parser = subparsers.add_parser('config', help='Gerencia configurações do projeto.')
    config_parser.add_argument('--home', help='O diretório principal do projeto (pasta atual, por padrão).')
    config_parser.add_argument('--global', '-g', dest='g', action='store_true', default=False, help='Guarda a configuração globalmente.')
    config_parser.add_argument('--unset', action='store_true', help='Apaga a configuração, se existir.')
    config_parser.add_argument('name', help='O nome da configuração.')
    config_parser.add_argument('value', nargs='?', help='O valor da configuração.')

    # Sub-comando: setup
    setup_parser = subparsers.add_parser('setup', help='Adiciona a ferramenta ao PATH.')
    setup_parser.add_argument('--remove', action='store_true', default=False, help='Use esta flag para remover a ferramenta do PATH.')

    args = parser.parse_args()

    if args.action == 'create':
        create_project(args)
        return
    
    if args.action == 'install':
        install_dependency(args)
        return

    if args.action == 'build':
        build_project(args)
        return

    if args.action == 'config':
        config(args)
        return

    if args.action == 'setup':
        remove: bool = args.remove
        file_path = os.path.expandvars(r'$localappdata\Microsoft\WindowsApps\t6modm.cmd')
        if remove:
            if not os.path.isfile(file_path):
                sys.stderr.write(f'[{RED}ERR!{RESET}] A ferramenta não está instalada.\r\n')
                sys.exit(1)

            os.unlink(file_path)
            print(f'[{GREEN}INFO{RESET}] A ferramenta foi removida do seu ambiente.')
            return

        if os.path.isfile(file_path):
            print(f'[{GREEN}INFO{RESET}] A ferramenta já está no seu ambiente, use {YELLOW}t6modm --help{RESET} para obter ajuda.')
            return

        with open(file_path, 'w') as file:
            file.write(f'@echo off\n"{sys.executable}" "{os.path.abspath(sys.argv[0])}" %*')

        print(f'[{GREEN}INFO{RESET}] A ferramenta foi adicionada ao seu ambiente.')

if __name__ == '__main__':
    main()