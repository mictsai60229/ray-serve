from apps.translator.app import Translator
from apps.greeting.app import Greeting

translator_app = Translator.bind()
greeting_app = Greeting.bind()
    