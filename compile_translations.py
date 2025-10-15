#!/usr/bin/env python3
import os
import sys
from babel.messages import catalog
from babel.messages import pofile

def compile_po_to_mo(po_file, mo_file):
    """Compile a .po file to .mo file"""
    with open(po_file, 'rb') as f:
        catalog_obj = pofile.read_po(f)
    
    with open(mo_file, 'wb') as f:
        catalog_obj.save(f)

def main():
    base_dir = "translations"
    
    for lang in ['hi', 'mr', 'ta']:
        po_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_path):
            print(f"Compiling {po_path} -> {mo_path}")
            compile_po_to_mo(po_path, mo_path)
        else:
            print(f"Warning: {po_path} not found")

if __name__ == "__main__":
    main()