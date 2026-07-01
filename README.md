# 🧠 AI Assistant — Умный помощник для программистов

AI Assistant — это локальный AI-помощник для программистов, который работает на основе RAG (Retrieval-Augmented Generation). Он отвечает на вопросы по документации, помогает писать и объяснять код.

---

## ✨ Возможности

- ✅ Ответы на вопросы по Python, Django, FastAPI, PostgreSQL
- ✅ Объяснение кода
- ✅ Генерация кода
- ✅ Работа с вашими скриптами и проектами
- ✅ Веб-интерфейс
- ✅ VS Code расширение
- ✅ Работает полностью локально (без интернета)

---

## 🛠️ Стек технологий

| Компонент | Технология |
|-----------|------------|
| **AI модель** | DeepSeek-Coder (локально через Ollama) |
| **Векторная БД** | ChromaDB |
| **Веб-интерфейс** | Streamlit |
| **VS Code расширение** | JavaScript + axios |
| **Язык** | Python 3.12+ |

---

## 🚀 Быстрый старт

### Установка

```bash
# Клонируй репозиторий
git clone https://github.com/AndreiAltyn282/ai-assistant.git
cd ai-assistant

# Создай виртуальное окружение
python3.12 -m venv venv
source venv/bin/activate

# Установи зависимости
pip install -r requirements.txt

# Скачай модель Ollama
ollama pull deepseek-coder:6.7b-instruct-q4_K_M
