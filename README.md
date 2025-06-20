# Multimodal-Jarvis

A Jarvis-like multimodal assistant system that integrates speech-to-text (STT), text-to-speech (TTS), and natural language processing (NLP) models. The system leverages state-of-the-art models from Hugging Face and provides both command-line and web-based interfaces.

## Features

- **Speech-to-Text (STT):** Converts spoken audio to text using Whisper.
- **Text-to-Speech (TTS):** Generates natural-sounding speech from text using SpeechT5.
- **Natural language processing:** (NLP) Supports advanced language understanding and generation.
- **Modular Design:** Easily extendable with new models and functionalities.
- **Web UI:** Gradio-based user interface for easy interaction.
- **API:** FastAPI backend for programmatic access.
- **Robust Logging:** Centralized logging and log rotation.
- **Async Database:** PostgreSQL support via SQLAlchemy async.

## Project Structure

```plaintext
Multimodal-Jarvis/
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── alembic.ini
├── data
│   ├── audio
│   │   └── bark_out.wav
│   ├── datasets
│   └── logs/
│       
├── docs
│   ├── README.md
│   ├── api_docs.md
│   └── setup_guide.md
├── main.py
├── models
│   ├── any-to-any
│   ├── nlp
│   │   └── Qwen2.5-1.5B-Instruct
│   ├── stt
│   │   └── whisper-large-v3-turbo
│   └── tts
│       └── Speecht5
├── pyproject.toml
├── requirements.txt
├── server.py
├── src
│   ├── auth
│   │   ├── base_config.py
│   │   ├── crud.py
│   │   ├── manager.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── babel.cfg
│   ├── config.py
│   ├── database.py
│   ├── gradio_ui.py
│   ├── i18n.py
│   ├── logger.py
│   ├── model.py
│   ├── pages
│   │   └── router.py
│   ├── static
│   │   ├── chatbot.jpg
│   │   ├── custom_gradio.css
│   │   ├── favicon.png
│   │   ├── favicon96.png
│   │   ├── register_login.js
│   │   ├── static.css
│   │   ├── static_auth.css
│   │   └── user.jpg
│   ├── templates
│   │   ├── main_page.html
│   │   └── userpage.html
│   └── translations
│       ├── en
│       │   └── LC_MESSAGES
│       │       ├── messages.mo
│       │       └── messages.po
│       ├── messages.pot
│       └── uk
│           └── LC_MESSAGES
│               ├── messages.mo
│               └── messages.po
├── ssl
│   ├── cert.pem
│   └── key.pem
├── tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_gradio.ipynb
│   └── test_main.py
└── uv.lock
```
## Installation


1. Clone the repository:
```bash
git clone https://github.com/your-org/Multimodal-Jarvis.git
cd Multimodal-Jarvis
```
2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  
# On Windows: 
.venv\Scripts\activate
uv pip install -r requirements.txt

```

3. initializes .env by config below
4. Database migration
```bash
alembic init alembic
```
Configure alembic.ini
Edit the line:

```ini
sqlalchemy.url = postgresql+asyncpg://DB_USER:DB_PASS@DB_HOST:DB_PORT/DB_NAME
```
Then in alembic/env.py add these lines in order to dynamically connect database schemas
```python
from src.config import database_settings as settings
from src.database import Base
from src.auth.models import *

config = context.config

section = config.config_ini_section
config.set_section_option(section, "POSTGRES_HOST", settings.POSTGRES_HOST)
config.set_section_option(section, "POSTGRES_PORT", settings.POSTGRES_PORT)
config.set_section_option(section, "POSTGRES_USER", settings.POSTGRES_USER)
config.set_section_option(section, "POSTGRES_NAME", settings.POSTGRES_NAME)
config.set_section_option(section, "POSTGRES_PASS", settings.POSTGRES_PASS)

target_metadata = Base.metadata
```
At last run this command to create a new migration script and apply it:
```bash
alembic revision --autogenerate -m "Your migration"
alembic upgrade head
```
## Config

### database.env
```plaintext
POSTGRES_HOST=localhost or postgres for docker # Database host
POSTGRES_PORT=5432 # Database port
POSTGRES_NAME= # Database name
POSTGRES_USER= # Database user
POSTGRES_PASS= # Database password
```

### production.env
```plaintext
SECRET_AUTH= # Secret key for authentication
HF_TOKEN= # Hugging Face token for model access
```

## Docker
To run the application using Docker, you can use the provided `docker-compose.yml` file. Make sure to have Docker and Docker Compose installed.

1. Build and run the Docker containers:
```bash
docker compose --env-file ./env/database.env --env-file ./env/production.env -f ./Docker/docker-compose.yml build
```

2. Deploy the application:
```bash
docker compose --env-file ./env/database.env --env-file ./env/production.env -f ./Docker/docker-compose.yml up -d```
```
## Contributing
Contributions are welcome! Please open issues or submit pull requests.

## License
This project is licensed under the terms of the LICENSE.

## Acknowledgements

- [Hugging Face Transformers](https://huggingface.co/transformers)

- [Gradio](https://www.gradio.app/)

- [SQLAlchemy](https://www.sqlalchemy.org/)
