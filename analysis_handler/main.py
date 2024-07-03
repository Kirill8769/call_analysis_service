import asyncio
from random import randint

from analysis_handler.gpt_handler import GPTHandler
from db.db_analysis_data import AnalysisData
from db.db_call_data import CallData
from loggers import logger


async def main():
    print("START")
    logger.info("[+] Start analysis handler")
    analysis_db = AnalysisData()
    gpt_handler = GPTHandler()
    call_db = CallData()
    await call_db.create_tables()

    while True:
        try:
            list_id_calls_for_analysis = await call_db.get_calls_for_analysis()
            if not list_id_calls_for_analysis:
                logger.info("[PAUSE] list_id_calls_for_analysis is empty, analysis_handler sleep 5min")
                await asyncio.sleep(300)
                continue
            for call_id in list_id_calls_for_analysis:
                transcription = await analysis_db.get_transcription_text(call_id)
                if transcription:
                    logger.info(f"[+] Начинаем анализ звонка {call_id}")

                    while True:
                        gpt_answer = await gpt_handler.get_gpt_response(promt=transcription)
                        if gpt_answer is not None:
                            logger.info(f"[+] Анализ звонка {call_id} успешно завершен")
                            await asyncio.sleep(randint(5, 15))
                            break
                        logger.info(f"[+] Ошибка при анализе звонка {call_id}, запускаем повторно")
                        await asyncio.sleep(randint(15, 25))
                    # if result_gpt_analysis["result"]:
                    #     analysis_result = result_gpt_analysis["result"]
                    #     if await analysis_db.update_general_analysis_data(call_id, analysis_result):
                    #         if await analysis_db.insert_evaluations_analysis(call_id, analysis_result):
                    #             if await analysis_db.insert_commentary_analysis(call_id, analysis_result):
                    #                 await call_db.update_status(call_id, "ANALYSIS_STATUS", "[OK_TEST]")
                    # elif result_gpt_analysis["error"]:
                    #     if await analysis_db.update_error_data(call_id, result_gpt_analysis["error"]):
                    #         await call_db.update_status(call_id, "ANALYSIS_STATUS", "[ERROR_TEST]")
                else:
                    logger.warning(f"[+] Звонок {call_id} помечен, но транскрибации нет")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}")


if __name__ == "__main__":
    asyncio.run(main())
