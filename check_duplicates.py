import os
import hashlib
from pathlib import Path

def get_file_hash(filepath):
    """Вычисляет MD5 хеш файла"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def find_duplicates(directory):
    """Находит дубликаты в папке"""
    hashes = {}
    duplicates = []

    for filepath in Path(directory).rglob('*.txt'):
        if filepath.is_file():
            file_hash = get_file_hash(filepath)
            if file_hash in hashes:
                duplicates.append((hashes[file_hash], filepath))
            else:
                hashes[file_hash] = filepath

    return duplicates

if __name__ == "__main__":
    directory = "rag_texts"
    dups = find_duplicates(directory)

    if dups:
        print(f"🔴 Найдено {len(dups)} дубликатов:")
        for dup in dups:
            print(f"  - {dup[0]}")
            print(f"    {dup[1]}")
    else:
        print("✅ Дубликатов не найдено!")
