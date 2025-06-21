from YP.logger import logger


def catalog_sync_wrapper(customer_id):
    from .get_from_sbis import catalog_sync
    logger.debug('Запускаю catalog_sync в режиме фоновой задачи Q-claster')
    catalog_sync(customer_id)
