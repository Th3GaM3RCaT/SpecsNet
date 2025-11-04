import subprocess

def get_from_inform(objeto="Card name:"):
    """
    Extrae información del reporte DirectX.
    
    Args:
        objeto: Texto a buscar en el reporte (ej: "Card name:", "Processor:")
    
    Returns:
        Lista de valores encontrados
    """
    try:
        # Generar reporte DirectX
        subprocess.check_output(
            ["dxdiag", "/t", "dxdiag_output.txt"],
            text=True
        )
        
        # Leer y parsear
        with open("dxdiag_output.txt", "r", encoding="cp1252") as f:
            lines = f.readlines()
        
        resultados = []
        for line in lines:
            if objeto in line:
                resultados.append(line.split(":", 1)[1].strip())
        
        return resultados
    except Exception:
        return []

if __name__ == "__main__":
    print(get_from_inform())
