import os
import sys
import chromadb
import ollama
from datetime import datetime
from pathlib import Path

# === НАСТРОЙКИ ===
MODEL_NAME = "deepseek-coder:6.7b-instruct-q4_K_M"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "python_docs"
SCRIPTS_DIR = "my_scripts"  # Папка с твоими скриптами

# === КЛАСС RAG-ПАЙПЛАЙНА ===
class RAGPipeline:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.history = []
    
    # === ШАГ 1: ПОИСК В БАЗЕ ===
    def search(self, query, n_results=5):
        print(f"🔍 Поиск в базе знаний...")
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0], results['metadatas'][0]
    
    # === ШАГ 2: ФОРМИРОВАНИЕ ПРОМПТА (УЛУЧШЕННЫЙ) ===
    def build_prompt(self, query, context_docs):
        context_text = "\n\n---\n\n".join(context_docs)
        
        prompt = f"""Ты — профессиональный AI-ассистент для программистов.
Отвечай подробно, структурированно и с примерами кода, если это уместно.

=== КОНТЕКСТ ИЗ ДОКУМЕНТАЦИИ ===
{context_text}

=== ВОПРОС ПОЛЬЗОВАТЕЛЯ ===
{query}

=== ТВОЙ ОТВЕТ ===
Дай развернутый, полезный и структурированный ответ.
Если вопрос просит код — покажи пример с пояснениями.
Если в контексте нет информации — честно скажи об этом.
"""
        return prompt
    
    # === ШАГ 3: ГЕНЕРАЦИЯ КОДА ===
    def generate(self, prompt):
        print(f"🤖 Генерация ответа через {MODEL_NAME}...")
        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Ты эксперт по Python и программированию. Отвечай точно, подробно и по делу."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.3,
                    "num_predict": 1500,
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"❌ Ошибка генерации: {e}"
    
    # === ПОЛНЫЙ ПАЙПЛАЙН ===
    def ask(self, query):
        print("\n" + "="*60)
        print(f"❓ Вопрос: {query}")
        print("="*60)
        
        # Шаг 1: Поиск
        docs, metadatas = self.search(query)
        
        # Шаг 2: Формирование промпта
        prompt = self.build_prompt(query, docs)
        
        # Шаг 3: Генерация
        answer = self.generate(prompt)
        
        # Сохраняем историю
        self.history.append({
            "query": query,
            "answer": answer,
            "sources": metadatas,
            "timestamp": datetime.now().isoformat()
        })
        
        print("\n" + "="*60)
        print("🤖 ОТВЕТ:")
        print("="*60)
        print(answer)
        print("\n" + "="*60)
        print("📚 ИСТОЧНИКИ:")
        for i, meta in enumerate(metadatas):
            print(f"  {i+1}. {meta.get('source', 'unknown')}")
        print("="*60)
        
        return answer
    
    # === ЗАГРУЗКА СВОИХ СКРИПТОВ ===
    def load_scripts(self, scripts_dir=SCRIPTS_DIR):
        if not os.path.exists(scripts_dir):
            print(f"❌ Папка {scripts_dir} не найдена!")
            return
        
        print(f"📂 Загрузка скриптов из {scripts_dir}...")
        script_files = []
        
        for ext in ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.go', '*.rs']:
            script_files.extend(Path(scripts_dir).glob(ext))
        
        if not script_files:
            print(f"❌ Не найдено скриптов в {scripts_dir}")
            return
        
        for script_path in script_files:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Добавляем в ChromaDB
                doc_id = f"script_{script_path.stem}"
                self.collection.add(
                    documents=[content],
                    metadatas=[{"source": str(script_path), "type": "script"}],
                    ids=[doc_id]
                )
                print(f"  ✅ Загружен: {script_path.name}")
            
            except Exception as e:
                print(f"  ❌ Ошибка {script_path.name}: {e}")
        
        print(f"✅ Загружено {len(script_files)} скриптов")
        print(f"   Всего документов: {self.collection.count()}")

# === ИНТЕРАКТИВНЫЙ РЕЖИМ ===
def interactive_mode():
    pipeline = RAGPipeline()
    print("🚀 RAG-пайплайн запущен!")
    print(f"📚 Документов в базе: {pipeline.collection.count()}")
    print("\nКоманды:")
    print("  /load_scripts - загрузить свои скрипты")
    print("  /history - показать историю")
    print("  /clear - очистить историю")
    print("  /exit - выход")
    print("\n" + "="*60)
    
    while True:
        query = input("\n❓ Введите вопрос (или команду): ").strip()
        
        if not query:
            continue
        
        if query.lower() == '/exit':
            print("👋 До свидания!")
            break
        
        elif query.lower() == '/load_scripts':
            pipeline.load_scripts()
            continue
        
        elif query.lower() == '/history':
            if not pipeline.history:
                print("📭 История пуста")
            else:
                print("\n📜 ИСТОРИЯ:")
                for i, item in enumerate(pipeline.history[-5:], 1):
                    print(f"{i}. {item['query'][:50]}... ({item['timestamp'][:16]})")
            continue
        
        elif query.lower() == '/clear':
            pipeline.history = []
            print("✅ История очищена")
            continue
        
        # Обычный вопрос
        pipeline.ask(query)

# === ЗАГРУЗКА СКРИПТОВ ИЗ КОМАНДНОЙ СТРОКИ ===
def load_scripts_mode():
    pipeline = RAGPipeline()
    pipeline.load_scripts()
    print(f"\n📚 Всего документов: {pipeline.collection.count()}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--load-scripts":
        load_scripts_mode()
    else:
        interactive_mode()
