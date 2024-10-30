from loguru import logger as logging
from colorama import init

# Инициализация colorama
init(autoreset=True)

# Настройка логирования
logging.add("bot.log", rotation="1 MB")  # Логирование в файл с ротацией
logging.remove()  # Удаление стандартного обработчика

# Добавление цветного обработчика
(logging.add(
    lambda msg: print(msg, end=""),  # Печатаем сообщение
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{module: >10}</cyan> : "
           "<yellow>{function: <15}</yellow> - "
           "<level>{message: <40}</level>"
))
