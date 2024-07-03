from loggers import logger
from db.db_connector import BaseConnector


class GeneralDB(BaseConnector):

    async def get_calls_data_for_send_bitrix(self) -> list | list[dict]:
        """
        Метод получает список словарей со всей необходимой информацией для дальнейшей передачи.
        Выборка производится по записям, которые ещё не переавались в Битрикс24.

        :return: Список словарей с данными.
        """
        result_list = []
        try:
            await self.connect()
            response_db = await self.connection.fetch(
                """
                SELECT 
                    b24_calls.*,                     
                    call_analysis.GENERAL_COMMENT,
                    call_analysis.CALL_QUALITY,
                    call_analysis.RESUME_MANAGER,
                    call_analysis.RECOMMENDATIONS
                FROM 
                    b24_calls
                JOIN 
                    call_analysis USING(call_id)
                WHERE 
                    b24_calls.ANALYSIS_STATUS IS NOT NULL AND b24_calls.SEND_STATUS IS NULL
                """
            )
            result_list = [dict(row) for row in response_db]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return result_list
