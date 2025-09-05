#!/usr/bin/env python3
import os
from babel.messages import pofile, mofile

# Pasta raiz do projeto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(PROJECT_ROOT, "src", "locales")

def compile_po_to_mo(locales_dir: str = LOCALES_DIR):
    """
    Compila todos os arquivos .po dentro de locales/ para .mo
    """
    for root, _, files in os.walk(locales_dir):
        for f in files:
            if f.endswith(".po"):
                po_path = os.path.join(root, f)
                mo_path = os.path.splitext(po_path)[0] + ".mo"

                with open(po_path, "rb") as po_file:
                    catalog = pofile.read_po(po_file)

                with open(mo_path, "wb") as mo_file:
                    mofile.write_mo(mo_file, catalog)

                print(f"✔ Compiled: {mo_path}")

if __name__ == "__main__":
    compile_po_to_mo()