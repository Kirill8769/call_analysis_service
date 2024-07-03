import json

from asyncpg.exceptions import UniqueViolationError
from loggers import logger
from db.db_connector import BaseConnector


class AnalysisData(BaseConnector):
    """Класс для работы с таблицами, хранящими в себе данные обработки и оценки звонков."""

    async def set_transcription(self, call_id: str, transcription_result: dict) -> bool:
        """
        Метод принимает результат транскрибации звонка и записывает его в БД.

        :param call_id: Id обработанного звонка.
        :param transcription_result: Результат транскрибации звонка.
        :return: Если запись прошла успешно, то возвращает True, в противном случае False.
        """
        await self.connect()
        rec_result = False
        try:
            segments = json.dumps(transcription_result["segments"])
            await self.connection.execute(
                "INSERT INTO call_analysis (CALL_ID, TRANSCRIBE_CALL, SEGMENTS) VALUES ($1, $2, $3)",
                call_id, transcription_result["text"], segments
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'[+] В БД добавлены результаты транскрибации звонка ({call_id})')
            rec_result = True
        finally:
            await self.connection.close()
            return rec_result

    async def get_transcription_text(self, call_id: str) -> str:
        """
        Метод возвращает текст транскрибации звонка по полученному call_id.

        :param call_id: id звонка.
        :return: Текст транскрибации звонка.
        """
        await self.connect()
        result_str = ""
        try:
            result = await self.connection.fetchrow(
                "SELECT TRANSCRIBE_CALL FROM call_analysis WHERE CALL_ID = $1", call_id,
            )
            if result:
                result_str = result["transcribe_call"]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return result_str

    async def update_general_analysis_data(self, call_id: str, data: list) -> bool:
        """
        Метод принимает результат анализа звонка и записывает его в БД.

        :param call_id: Id обработанного звонка.
        :param data: Словарь с результатами анализа звонка.
        :return: Если запись прошла успешно, то возвращает True, в противном случае False.
        """
        await self.connect()
        rec_result = False
        try:
            resume = "\n".join([f"- {text}" for text in data[10]["resume manager"]])
            recommendations = "\n".join([f"- {text}" for text in data[11]["recommendations"]])
            await self.connection.execute("""
                UPDATE call_analysis
                SET GENERAL_COMMENT = $1,
                CALL_QUALITY = $2,
                RESUME_MANAGER = $3,
                RECOMMENDATIONS = $4
                WHERE CALL_ID = $5
            """, data[0]["general comment"], data[0]["total score"], resume, recommendations, call_id)
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'[+] В БД добавлены общие результаты анализа звонка ({call_id})')
            rec_result = True
        finally:
            await self.connection.close()
            return rec_result

    async def update_error_data(self, call_id: str, error: str) -> bool:
        """
        Метод принимает результат анализа звонка и записывает его в БД.

        :param call_id: Id обработанного звонка.
        :param error: Текст ошибки.
        :return: Если запись прошла успешно, то возвращает True, в противном случае False.
        """
        await self.connect()
        rec_result = False
        try:
            await self.connection.execute(
                "UPDATE call_analysis SET GENERAL_COMMENT = $1 WHERE CALL_ID = $2", error, call_id
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'[+] В БД добавлены данные об ошибке ({call_id})')
            rec_result = True
        finally:
            await self.connection.close()
            return rec_result

    async def insert_evaluations_analysis(self, call_id: str, data: list) -> bool:
        """
        Метод принимает результат анализа звонка и записывает его в БД.

        :param call_id: Id обработанного звонка.
        :param data: Словарь с результатами анализа звонка.
        :return: Если запись прошла успешно, то возвращает True, в противном случае False.
        """
        await self.connect()
        rec_result = False
        try:
            record_availability = await self.connection.fetchrow(
                "SELECT * FROM evaluations WHERE CALL_ID = $1", call_id
            )
            if record_availability:
                raise UniqueViolationError(f"Результаты звонка {call_id} уже были записаны в таблицу ранее")
            await self.connection.execute(
                """
                INSERT INTO evaluations (CALL_ID, GREETING, SPEECH, INITIATIVE,
                NEED, OFFER, OBJECTION, PERSEVERANCE, ADVANTAGES, AGREEMENT) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)           
                """,
                call_id, data[1]["greeting"]["score"], data[2]["speech"]["score"],
                data[3]["initiative"]["score"], data[4]["need"]["score"],
                data[5]["offer"]["score"], data[6]["objection"]["score"],
                data[7]["perseverance"]["score"], data[8]["advantages"]["score"],
                data[9]["agreement"]["score"]
            )
        except UniqueViolationError as uniq_ex:
            logger.warning(f"{uniq_ex.__class__.__name__}: {uniq_ex}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'[+] В БД добавлены оценки параметров анализа звонка ({call_id})')
            rec_result = True
        finally:
            await self.connection.close()
            return rec_result

    async def insert_commentary_analysis(self, call_id: str, data: list) -> bool:
        """
        Метод принимает результат анализа звонка и записывает его в БД.

        :param call_id: Id обработанного звонка.
        :param data: Словарь с результатами анализа звонка.
        :return: Если запись прошла успешно, то возвращает True, в противном случае False.
        """
        await self.connect()
        rec_result = False
        try:
            record_availability = await self.connection.fetchrow("SELECT * FROM commentary WHERE CALL_ID = $1", call_id)
            if record_availability:
                raise UniqueViolationError(f"Результаты звонка {call_id} уже были записаны в таблицу ранее")
            await self.connection.execute(
                """
                INSERT INTO commentary (CALL_ID, GREETING, SPEECH, INITIATIVE,
                NEED, OFFER, OBJECTION, PERSEVERANCE, ADVANTAGES, AGREEMENT) 
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)           
                """,
                call_id, data[1]["greeting"]["comment"], data[2]["speech"]["comment"],
                data[3]["initiative"]["comment"], data[4]["need"]["comment"],
                data[5]["offer"]["comment"], data[6]["objection"]["comment"],
                data[7]["perseverance"]["comment"], data[8]["advantages"]["comment"],
                data[9]["agreement"]["comment"]
            )
        except UniqueViolationError as uniq_ex:
            logger.warning(f"{uniq_ex.__class__.__name__}: {uniq_ex}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'[+] В БД добавлены комментарии параметров анализа звонка ({call_id})')
            rec_result = True
        finally:
            await self.connection.close()
            return rec_result
