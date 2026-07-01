#!/bin/bash
echo "📚 Скачивание документации..."

# Python
echo "🐍 Python..."
mkdir -p rag_docs/python
cp -r python_html_docs/* rag_docs/python/ 2>/dev/null

# Django
echo "🌐 Django..."
mkdir -p rag_docs/django
wget -q -O rag_docs/django/django.txt https://docs.djangoproject.com/en/5.0/ 2>/dev/null || echo "⚠️ Django не скачался"

# FastAPI
echo "⚡ FastAPI..."
mkdir -p rag_docs/fastapi
wget -q -O rag_docs/fastapi/fastapi.txt https://fastapi.tiangolo.com/ 2>/dev/null || echo "⚠️ FastAPI не скачался"

# PostgreSQL
echo "🐘 PostgreSQL..."
mkdir -p rag_docs/postgresql
wget -q -O rag_docs/postgresql/postgresql.txt https://www.postgresql.org/docs/current/index.html 2>/dev/null || echo "⚠️ PostgreSQL не скачался"

# Docker
echo "🐳 Docker..."
mkdir -p rag_docs/docker
wget -q -O rag_docs/docker/docker.txt https://docs.docker.com/ 2>/dev/null || echo "⚠️ Docker не скачался"

# Создаём файл с описанием библиотек
echo "📦 Создание списка библиотек..."
cat > rag_docs/my_libraries.txt << 'LIBEOF'
Мои любимые библиотеки Python:

1. Django - веб-фреймворк для создания сложных приложений
2. FastAPI - современный фреймворк для API
3. SQLAlchemy - ORM для работы с базами данных
4. Pydantic - валидация данных
5. Celery - асинхронные задачи
6. Redis - кеширование и брокер
7. PostgreSQL - основная БД
8. Docker - контейнеризация
LIBEOF

echo "✅ Все документы скачаны!"
