import os
import uuid

import requests
from dotenv import load_dotenv

from loggers import logger


class BitrixPost:
    """Класс для взаимодействия с API Bitrix24 и получения информации."""

    def __init__(self) -> None:
        load_dotenv()
        self.__webhook = os.getenv("BITRIX_WEBHOOK")
        self.__portal = os.getenv("BITRIX_URL")
        self.methods = {
            "add_element": "lists.element.add",
            "update_element": "lists.element.update",
        }

    def post_element(self, call_analysis_info: dict) -> bool:
        """
        Метод публикует результаты оценки качества звонка в Битрикс24.

        :param call_analysis_info: Словарь с результатами оценки звонка.
        :return: Возвращает True, если публикация данных прошла успешно, в противном случае, возвращает False.
        """
        status_result = False
        method = self.methods["add_element"]
        element_code = uuid.uuid4()
        url = f"{self.__portal}/rest/{self.__webhook}/{method}.json"
        params = {
            "IBLOCK_ID": 110,
            "IBLOCK_TYPE_ID": "bitrix_processes",
            "ELEMENT_CODE": element_code,
            "FIELDS[NAME]": f'Оценка качества {call_analysis_info["call_id"]}',
            "FIELDS[PROPERTY_1022]": element_code,
            "FIELDS[PROPERTY_1012]": call_analysis_info["call_id"],
            "FIELDS[PROPERTY_1025]": call_analysis_info["analysis_status"],
            "FIELDS[PROPERTY_1021]": call_analysis_info["manager_id"],
            "FIELDS[PROPERTY_1013]": call_analysis_info["type"],
            "FIELDS[PROPERTY_1014]": call_analysis_info["date"],
            "FIELDS[PROPERTY_1015]": call_analysis_info["duration_visual"],
            "FIELDS[PROPERTY_1016]": call_analysis_info["deal_url"],
            "FIELDS[PROPERTY_1017]": call_analysis_info["stage"],
            "FIELDS[PROPERTY_1018]": call_analysis_info["call_quality"],
            "FIELDS[PROPERTY_1024]": call_analysis_info["general_comment"],
            "FIELDS[PROPERTY_1019]": call_analysis_info["resume_manager"],
            "FIELDS[PROPERTY_1020]": call_analysis_info["recommendations"],
        }
        try:
            response = requests.post(url=url, params=params)
            if response.status_code == 200:
                status_result = True
            else:
                logger.error(f"Ошибка при выполнении запроса. Код состояния: {response.status_code}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'Результаты анализа звонка ({call_analysis_info["call_id"]}) успешно переданы в битрикс')
        finally:
            return status_result
