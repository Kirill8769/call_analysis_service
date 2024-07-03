import os

import requests
from dotenv import load_dotenv

from config import PATH_PROJECT
from loggers import logger


class BitrixGet:
    """Класс для взаимодействия с API Bitrix24 и получения информации."""

    def __init__(self) -> None:
        load_dotenv()
        self.__webhook = os.getenv("BITRIX_WEBHOOK")
        self.__portal = os.getenv("BITRIX_URL")
        self.methods = {
            "call_list": "voximplant.statistic.get",
            "deal_list": "crm.deal.list",
            "deal_info": "crm.deal.get",
            "file_info": "disk.file.get",
            "user_info": "user.get",
        }

    def get_response(self, url: str | None = None, method: str = None, params: dict = None) -> requests.Response | None:
        """
        Выполняет GET-запрос к API Bitrix.

        :param url: URL для запроса. Если не указан, используется стандартный URL.
        :param method: Метод API.
        :param params: Параметры запроса.
        :return: Возвращаем ответ сайта.
        """
        result = None
        if url is None:
            url = f"{self.__portal}/rest/{self.__webhook}/{method}.json"
        try:
            response = requests.get(url=url, params=params)
            if response.status_code == 200:
                result = response
            else:
                logger.error(f"Ошибка при выполнении запроса. Код состояния: {response.status_code}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return result

    def get_user_data(self, user_id: str) -> list[dict] | None:
        """
        Получает информацию о сотруднике по API Bitrix.

        :param user_id: id сотрудника.
        :return: Словарь с полученной информацией.
        """
        result = None
        params = {"ID": user_id}
        method = self.methods["user_info"]
        try:
            response_data = self.get_response(method=method, params=params).json()
            if response_data:
                result = response_data["result"]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return result

    def get_call_list(self, start_date: str) -> list[dict] | None:
        """
        Получает информацию о звонках по API Bitrix.

        :param start_date: Указываем с какой даты начинаем собирать записи.
        :return: Результат запроса в виде JSON списка со звонками.
        """
        result = None
        params = {"filter[>=CALL_START_DATE]": start_date, "SORT": "ID", "ORDER": "ASC"}
        method = self.methods["call_list"]
        try:
            response_data = self.get_response(method=method, params=params).json()
            if response_data:
                result = response_data["result"]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return result

    def get_deal_id(self, entity_type: str, entity_id: str) -> str | None:
        """
        Получает id сделки по API Bitrix.

        :param entity_type: Тип сущности (например, 'LEAD').
        :param entity_id: id сущности.
        :return: id сделки или None.
        """
        result = None
        crm_entity_type = f"filter[{entity_type}_ID]"
        crm_entity_id = int(entity_id)
        params = {crm_entity_type: crm_entity_id}
        method = self.methods["deal_list"]
        try:
            response_data = self.get_response(method=method, params=params).json()
            if response_data["result"]:
                result = response_data["result"][0]["ID"]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return result

    def get_deal_stage(self, deal_id: str) -> str | None:
        """
        Получает стадию сделки по API Bitrix.

        :param deal_id: id сделки.
        :return: Статус сделки или None.
        """
        result = None
        params = {"ID": deal_id}
        method = self.methods["deal_info"]
        try:
            response_data = self.get_response(method=method, params=params).json()
            if response_data:
                result = response_data["result"]["STAGE_ID"]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return result

    def get_filename(self, call_id: int) -> str | None:
        """
        Получает имя файла и ссылку для скачивания по API Bitrix.

        :param call_id: id звонка.
        :return: Если запись звонка успешно сохранена, то возвращает имя файла, иначе, возвращает None.
        """
        result = None
        method = self.methods["file_info"]
        params = {"id": call_id}
        try:
            response_data = self.get_response(method=method, params=params).json()
            if response_data["result"]:
                response_name = response_data["result"]["NAME"]
                filename = f"{call_id}_{response_name}"
                download_url = response_data["result"]["DOWNLOAD_URL"]
                save_result = self.saved_file(download_url, filename)
                if save_result:
                    result = filename
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return result

    def saved_file(self, download_url: str, filename: str) -> bool:
        """
        Получает запись звонка по API Bitrix и сохраняет её на локальный диск

        :param download_url: Ссылка для скачивания файла.
        :param filename: Имя файла.
        :return: Возвращает True или False, в зависимости от того,
        успешно или нет прошла запись файла на локальный диск.
        """
        save_result = False
        output_path = os.path.join(PATH_PROJECT, "audio")
        if not os.path.exists(output_path):
            raise FileExistsError("Папка, для сохранения записей, не найдена")
        try:
            response_file = self.get_response(url=download_url)
            if response_file is not None:
                with open(f"{output_path}/{filename}", "wb") as file:
                    file.write(response_file.content)
        except FileExistsError as file_ex:
            logger.error(f"{file_ex.__class__.__name__}: {file_ex}", exc_info=True)
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f"[+] Запись разговора {filename} успешно скачана")
            save_result = True
        finally:
            return save_result
