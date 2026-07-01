import os
from pathlib import Path

REPOS_DIR = "github_repos"
OUTPUT_DIR = "rag_texts"

def is_code_file(filename):
    extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']
    return any(filename.endswith(ext) for ext in extensions)

def extract_code_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def process_repos():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = 0

    for repo_path in Path(REPOS_DIR).iterdir():
        if not repo_path.is_dir():
            continue
        
        repo_name = repo_path.name
        print(f"📁 Обработка: {repo_name}")
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and is_code_file(file_path.name):
                code = extract_code_content(file_path)
                
                if len(code.strip()) > 50:
                    rel_path = file_path.relative_to(repo_path)
                    txt_name = f"{repo_name}_{str(rel_path).replace('/', '_')}.txt"
                    txt_path = os.path.join(OUTPUT_DIR, txt_name[:200])
                    
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(f"=== {repo_name}/{rel_path} ===\n\n{code}")
                    
                    total += 1
        
        print(f"  ✅ Добавлено файлов: {total}")

    print(f"\n✅ Обработано {total} файлов из репозиториев")

if __name__ == "__main__":
    process_repos()
