#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reparar archivos de capas que perdieron el wrapper JavaScript.
Detecta archivos que contienen GeoJSON crudo sin la declaración var necesaria.
"""

import os
import json
import re
from pathlib import Path

def get_var_name(filename):
    """Extraer el nombre de variable basado en el nombre del archivo."""
    # Remover .js extension
    name = filename[:-3]
    # Crear variable válida: geo_nombre
    return f"geo_{name}"

def is_valid_js_wrapper(content):
    """Verificar si el archivo ya tiene un wrapper JavaScript válido."""
    stripped = content.strip()
    return stripped.startswith('var ')

def has_valid_json(content):
    """Verificar si el contenido es JSON válido."""
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False

def fix_layer_file(filepath):
    """Reparar un archivo de capa añadiendo el wrapper JavaScript."""
    print(f"Procesando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Si ya tiene wrapper, saltar
    if is_valid_js_wrapper(content):
        print(f"  ✓ Ya tiene wrapper correcto")
        return False
    
    # Verificar si es JSON válido
    if not has_valid_json(content):
        print(f"  ✗ No es JSON válido")
        return False
    
    # Extraer nombre de variable
    filename = os.path.basename(filepath)
    var_name = get_var_name(filename)
    
    # Crear nuevo contenido con wrapper
    new_content = f"var {var_name} = {content};"
    
    # Guardar archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ Reparado: var {var_name} = ... ;")
    return True

def main():
    layers_dir = Path(__file__).parent / "layers"
    
    if not layers_dir.exists():
        print(f"ERROR: No se encontró el directorio: {layers_dir}")
        return
    
    print(f"Buscando archivos de capas en: {layers_dir}\n")
    
    js_files = sorted(layers_dir.glob("*.js"))
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filepath in js_files:
        # Saltar archivos especiales
        if filepath.name in ['layers.js', 'legend.js']:
            print(f"Saltando: {filepath.name} (archivo especial)")
            skipped_count += 1
            continue
        
        try:
            if fix_layer_file(str(filepath)):
                fixed_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMEN:")
    print(f"  Archivos reparados: {fixed_count}")
    print(f"  Archivos saltados: {skipped_count}")
    print(f"  Errores: {error_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
