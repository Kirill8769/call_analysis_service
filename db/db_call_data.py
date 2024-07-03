import os
from datetime import timedelta

from loggers import logger
from db.db_connector import BaseConnector


class CallData(BaseConnector):
    """Работает со звонками."""

    async def insert_data(
            self,
            call: dict,
            portal_user_name: str,
            deal_id: None | str,
            file_name: str,
            deal_stage: None | str
    ) -> None:
        """
        Вставляет данные о звонке в базу данных.

        :param call: Информация о звонке.
        :param portal_user_name: Фамилия, имя сотрудника.
        :param deal_id: Идентификатор сделки.
        :param file_name: Имя файла записи звонка.
        :param deal_stage: Стадия сделки.
        """
        await self.connect()
        try:
            portal = os.getenv('BITRIX_URL')
            deal_url = f"{portal}/crm/deal/details/{deal_id}/" if deal_id else None
            duration_visual = str(timedelta(seconds=float(call["CALL_DURATION"])))
            if call["CALL_TYPE"] == "1":
                call_type = "Исходящий"
            elif call["CALL_TYPE"] == "2":
                call_type = "Входящий"
            else:
                call_type = call["CALL_TYPE"]

            await self.connection.execute(
                """INSERT INTO b24_calls (
                CALL_ID, STAGE, MANAGER_ID, PORTAL_USER_NAME, RECORD_FILE_ID, TYPE, DATE,
                TIMEZONE, DURATION, DURATION_VISUAL, DEAL_ID, CRM_ENTITY_TYPE, CRM_ENTITY_ID, CRM_ACTIVITY_ID,
                PORTAL_NUMBER, PHONE_NUMBER, DEAL_URL, FILE_NAME)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)""",
                call["ID"],
                deal_stage,
                int(call["PORTAL_USER_ID"]),
                portal_user_name,
                call["RECORD_FILE_ID"],
                call_type,
                call["CALL_START_DATE"],
                "UTC",
                int(call["CALL_DURATION"]),
                duration_visual,
                deal_id,
                call["CRM_ENTITY_TYPE"],
                call["CRM_ENTITY_ID"],
                call["CRM_ACTIVITY_ID"],
                call["PORTAL_NUMBER"],
                call["PHONE_NUMBER"],
                deal_url,
                file_name,
            )
            logger.info(f"[+] В БД добавлена новая запись о звонке ({call['ID']})")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()

    async def get_id_calls(self) -> list | list[str]:
        """
        Получает последние 20 id звонков из базы данных.

        :return: Список последних id звонков.
        """
        id_calls = []
        try:
            await self.connect()
            result = await self.connection.fetch("SELECT CALL_ID FROM b24_calls ORDER BY ID DESC LIMIT 20")
            id_calls = [call_id["call_id"] for call_id in result]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return id_calls

    async def get_start_date(self) -> str:
        """
        Получает дату и время последнего звонка из базы данных.

        :return: Строка, представляющая дату и время последнего звонка.
        """
        result_date = ""
        try:
            await self.connect()
            result = await self.connection.fetchrow("SELECT DATE FROM b24_calls ORDER BY ID DESC LIMIT 1")
            if result:
                result_date = result["date"]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return result_date

    async def get_calls_for_transcription(self, count: int = 5) -> list[dict]:
        """
        Метод получает информацию о звонках из БД для дальнейшей транскрибации.

        :param count: Количество получаемых звонков.
        :return: Список словарей с информацией о звонках.
        """
        result = []
        try:
            await self.connect()
            result = await self.connection.fetch(
                f"SELECT * FROM b24_calls WHERE TRANSCRIBE_STATUS IS NULL LIMIT {count}"
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return result

    async def get_calls_for_analysis(self, count: int = 5) -> list | list[str]:
        """
        Метод получает список call_id из БД для дальнейшего анализа качества.

        :param count: Количество получаемых id.
        :return: Список id непроанализированных звонков
        """
        result_id = []
        try:
            await self.connect()
            result = await self.connection.fetch(
                f"""SELECT CALL_ID 
                FROM b24_calls 
                WHERE ANALYSIS_STATUS IS NULL AND TRANSCRIBE_STATUS IS NOT NULL 
                LIMIT {count}"""
            )
            result_id = [call["call_id"] for call in result]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return result_id

    async def update_status(self, call_id: str, name_column: str, status: str) -> None:
        """
        Метод обновляет статус в переданной колонке по id звонка в базе данных.

        :param call_id: Id звонка.
        :param name_column: Название колонки.
        :param status: Статус анализа звонка.
        """
        try:
            if name_column.upper() not in ["TRANSCRIBE_STATUS", "ANALYSIS_STATUS", "SEND_STATUS"]:
                raise ValueError("Изменить статус в переданной колонке нельзя")
            await self.connect()
            await self.connection.execute(
                f"UPDATE b24_calls SET {name_column} = $1 WHERE CALL_ID = $2", status, call_id,
            )
        except ValueError as val_ex:
            logger.warning(f"{val_ex.__class__.__name__}: {val_ex}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
