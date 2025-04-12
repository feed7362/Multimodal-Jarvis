import gettext

LANGUAGES = ["en", "ukr"]
current = "en"

translations = {
    lang: gettext.translation(
        "messages", localedir="translations", languages=[lang], fallback=True)
    for lang in LANGUAGES
}

def get_translator(lang: str):
    return translations.get(lang, translations['en'])

_ = get_translator(current).gettext

#pybabel extract -o translations/messages.pot i18n.py

#pybabel init -i translations/messages.pot -d translations -l en
#pybabel init -i translations/messages.pot -d translations -l ukr

#pybabel compile -d translations