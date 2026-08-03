#!/usr/bin/env python3
"""
Script para propagar citas de cartas anuales a páginas de conceptos relevantes
Este script ayuda a distribuir citas específicas de cartas anuales a las páginas
de conceptos apropiadas en el directorio wiki/Concepts/
"""

import os
import re
from pathlib import Path


def find_quote_passages(text, max_length=200):
    """
    Encuentra fragmentos de texto que podrían ser citas relevantes
    """
    # Buscar fragmentos entre comillas o después de ciertos indicadores
    quote_patterns = [
        r'"([^"]{20,200})"',  # Texto entre comillas dobles
        r"'([^']{20,200})'",  # Texto entre comillas simples
        r'>\s*"([^"]{20,200})"',  # Bloques de cita con comillas
    ]
    
    quotes = []
    for pattern in quote_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            quote = match.group(1).strip()
            if len(quote) > 20:  # Asegurar que sea lo suficientemente larga para ser significativa
                quotes.append(quote)
    
    return quotes


def propagate_quotes_to_concepts():
    """
    Propaga citas de cartas anuales a páginas de conceptos relevantes
    """
    # Directorios principales
    sources_dir = Path("wiki/Sources/")
    concepts_dir = Path("wiki/Concepts/")
    raw_dir = Path("Raw/")
    
    # Lista de archivos de fuentes (cartas anuales)
    source_files = list(sources_dir.glob("????ltr.md"))
    
    # Diccionario de relaciones concepto-carta para rastrear referencias
    concept_references = {}
    
    print("Iniciando propagación de citas...")
    
    for source_file in sorted(source_files):
        year = source_file.name[:4]
        print(f"\nProcesando carta de {year}: {source_file.name}")
        
        # Leer contenido de la carta
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer citas potenciales
        quotes = find_quote_passages(content)
        
        # Buscar conexiones con conceptos basados en palabras clave
        content_lower = content.lower()
        matched_concepts = []
        
        # Buscar archivos de conceptos que puedan estar relacionados
        for concept_file in concepts_dir.glob("*.md"):
            concept_name = concept_file.stem.lower()
            
            # Verificar si el nombre del concepto aparece en la carta
            if concept_name in content_lower:
                matched_concepts.append(concept_file.name)
                
                # Leer contenido del concepto
                with open(concept_file, 'r', encoding='utf-8') as cf:
                    concept_content = cf.read()
                
                # Agregar referencia a la carta actual si aún no existe
                if f"[[Sources/{year}ltr]]" not in concept_content:
                    # Encontrar posición para insertar la referencia
                    lines = concept_content.split('\n')
                    
                    # Buscar sección de referencias cruzadas o final del archivo
                    insert_pos = len(lines)
                    for i, line in enumerate(lines):
                        if line.strip().lower().startswith('cross-references'):
                            insert_pos = i + 1
                            break
                        elif line.strip().startswith('## ') and 'references' in line.lower():
                            insert_pos = i + 1
                            break
                    
                    # Insertar la referencia
                    if insert_pos == len(lines):
                        # Si no encontramos una sección específica, agregar al final
                        lines.extend(['', f"- [[Sources/{year}ltr]]"])
                    else:
                        # Buscar la lista y agregar la referencia
                        while insert_pos < len(lines) and lines[insert_pos].strip() != '':
                            insert_pos += 1
                        lines.insert(insert_pos, f"- [[Sources/{year}ltr]]")
                    
                    # Escribir el archivo actualizado
                    with open(concept_file, 'w', encoding='utf-8') as cf:
                        cf.write('\n'.join(lines))
                    
                    print(f"  - Añadida referencia a {concept_file.name} <- {source_file.name}")
        
        if matched_concepts:
            print(f"  - Conceptos coincidentes: {', '.join(matched_concepts)}")
        else:
            print(f"  - No se encontraron conceptos coincidentes")
    
    print("\nPropagación de citas completada.")


def main():
    """
    Función principal
    """
    print("Propagador de Citas - Warren Buffett Second Brain")
    print("=" * 50)
    
    # Verificar que los directorios existen
    sources_dir = Path("wiki/Sources/")
    concepts_dir = Path("wiki/Concepts/")
    
    if not sources_dir.exists():
        print(f"Error: Directorio {sources_dir} no encontrado")
        return
    
    if not concepts_dir.exists():
        print(f"Error: Directorio {concepts_dir} no encontrado")
        return
    
    # Ejecutar la propagación
    propagate_quotes_to_concepts()


if __name__ == "__main__":
    main()