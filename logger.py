from loguru import logger as logging
from colorama import init

# Инициализация colorama
init(autoreset=True)

logging.remove()  # Удаление стандартного обработчика
# Настройка логирования
logging.add("bot.log", rotation="1 MB", level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss,SSS} | {level: <8} | {module: >10} : {function: <15} - {message}")  # Логирование в файл с ротацией

# Добавление цветного обработчика
(logging.add(
    lambda msg: print(msg, end=""),  # Печатаем сообщение
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{module: >15}</cyan> : "
           "<yellow>{function: <20}</yellow> - "
           "<level>{message: <40}</level>"
))
