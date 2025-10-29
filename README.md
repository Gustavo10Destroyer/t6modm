# t6modm
Use `t6modm help` para ver a mensagem de ajuda.

Veja o projeto de exemplo para entender a estrutura da ferramenta.
Configure as seguintes variáveis de ambiente:
- `OAT_HOME` - Caminho para o [OAT](https://github.com/Laupetin/OpenAssetTools).
- `GAME_HOME` - Caminho para o diretório do jogo.

Essas variáveis podem ser configuradas globalmente através das Variáveis de Ambiente do Windows, e também podem ser configuradas localmente para o projeto atual através do arquivo `.t6modm.env`.

# Setup
You need have Python installed.

1. Install dependencies
```ps1
pip install -r requirements.txt
```

2. Run make.py
```ps1
python make.py
```

3. Add to environment
```ps1
python src/main.py
```

# How to remove from environment?
You could try `t6modm setup --remove`, if doesn't works, delete the file at `$env:LOCALAPPDATA\Microsoft\WindowsApps\t6modm.cmd` manually.