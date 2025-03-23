import os
from loguru import logger
# from notifiers.logging import NotificationHandler
# from dotenv import load_dotenv


logger.add(f'logs/log.log', rotation='20 mb', level="DEBUG")
logger.add(f'logs/info.log', rotation='20 mb', level="INFO")
logger.add(f'logs/warning.log', rotation='10 mb', level="WARNING")
logger.add(f'logs/errors.log', rotation='10 mb', level="ERROR")
logger.add(f'logs/critical.log', rotation='10 mb', level="CRITICAL")


# load_dotenv()

params = {
    "token": '7792267976:AAGQI0EBRaVnU9C1K9LQN9SNl9fskcIy0t4',
    "chat_id": 674796107,
}

# tg_handler = NotificationHandler(provider='telegram', defaults=params)
# logger.add(tg_handler, level='INFO')


if __name__ == "__main__":
    logger.debug("Уровень Debug")
    logger.info("Уровень Info")
    logger.warning("Уровень Warning")
    logger.error("Уровень Error")
    logger.critical("Уровень Critical Error")


