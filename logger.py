from loguru import logger as logging
from colorama import init

init(autoreset=True)

logging.remove()

logging.add(
    "bot.log",
    rotation="1 MB",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} | {level: <8} | {module: >10} : {function: <15} - {message}"
)

(logging.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{module: >15}</cyan> : "
           "<yellow>{function: <20}</yellow> - "
           "<level>{message: <40}</level>"
))
