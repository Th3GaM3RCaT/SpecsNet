#!/usr/bin/env python3
"""
Wrapper para ejecutar el servidor desde la raíz del proyecto.
Ejecuta: python src/servidor.py
"""

from sys import path
from pathlib import Path

# Agregar src/ al path de Python
src_dir = Path(__file__).parent / "src"
path.insert(0, str(src_dir))

# Importar y ejecutar el módulo servidor
if __name__ == "__main__":
    # Cambiar directorio de trabajo a src/
    from os import chdir

    chdir(src_dir)

    # Importar servidor como módulo y ejecutar main()
    from mainServidor import main
    main()
