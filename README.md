# t6modm
Uma ferramenta para tornar fácil a criação e compilação de mods de Call of Duty: Black Ops 2.
Usa [OAT](https://github.com/Laupetin/OpenAssetTools) para compilar.

# How To
A ferramenta é auto explicativa, algumas funcionalidades não estão prontas.
Use:
```sh
python main.py --help
```
para ver a mensagem de ajuda.

# Config
Para que um projeto seja compilável em vários ambientes, a ferramenta conta com variáveis, que você pode adicionar no projeto ou globalmente usando:
```sh
python main.py config minha.variavel.local "Valor da variável"
```

```sh
python main.py config --global GAME_DIR "C:/Caminho/absoluto/para/a/pasta/do/jogo"
```

### Variáveis
As variáveis são usadas no project.t6modm.json. Veja o mod de exemplo para mais detalhes.

# Configurar ferramenta no ambiente
Para instalar, use:
```sh
python main.py setup
```

E para remover, use:
```sh
python main.py setup --remove
```