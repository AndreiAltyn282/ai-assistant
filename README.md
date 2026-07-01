# 🧠 AI Assistant — Умный помощник для программистов

**AI Assistant** — это локальный AI-помощник для программистов, работающий на основе **RAG** (Retrieval-Augmented Generation). Он отвечает на вопросы по документации, помогает писать и объяснять код, используя вашу базу знаний.

---

## ✨ Возможности

- ✅ Ответы на вопросы по **Python, Django, FastAPI, PostgreSQL, Docker, Kubernetes**
- ✅ Объяснение кода построчно
- ✅ Генерация кода
- ✅ Работа с вашими скриптами и проектами
- ✅ Веб-интерфейс на Streamlit
- ✅ VS Code расширение (горячая клавиша `Ctrl+Shift+A`)
- ✅ Работает полностью локально (без интернета)
- ✅ Поддержка нескольких AI-моделей (DeepSeek-Coder, Llama 3.2, Mistral)

---

## 🛠️ Стек технологий

| Компонент | Технология |
|-----------|------------|
| **AI модель** | DeepSeek-Coder (локально через Ollama) |
| **Векторная БД** | ChromaDB |
| **Веб-интерфейс** | Streamlit |
| **VS Code расширение** | JavaScript + axios |
| **Язык** | Python 3.14 |

---

## 📚 База знаний

| Тип | Источник |
|-----|----------|
| **Python** | Официальная документация |
| **Django** | Официальная документация |
| **FastAPI** | Официальная документация |
| **PostgreSQL** | Официальная документация |
| **Docker** | Официальная документация |
| **Kubernetes** | Официальная документация |
| **Код библиотек** | Django, FastAPI, Pandas, NumPy, Requests, Flask |
| **Ваши скрипты** | Папка `my_scripts/` |

---

## 🚀 Быстрый старт

### Установка

```bash
# Клонируй репозиторий
git clone https://github.com/AndreiAltyn282/ai-assistant.git
cd ai-assistant

# Создай виртуальное окружение
python3.14 -m venv venv
source venv/bin/activate

# Установи зависимости
pip install -r requirements.txt

# Скачай модель Ollama
ollama pull deepseek-coder:6.7b-instruct-q4_K_M
