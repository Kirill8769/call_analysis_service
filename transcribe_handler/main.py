import asyncio

from db.db_call_data import CallData
from db.db_analysis_data import AnalysisData
from transcribe_handler.utils import get_transcription_whisper
from loggers import logger


async def main() -> None:
    """
    Основная функция, выполняет обработку звонков для транскрипции с помощью библиотеки Whisper и записывает
    результат в базу данных. Порядок работы:
    - Получает имя аудиофайла.
    - Вызывает функцию get_transcription_whisper для получения результата транскрипции.
    - Если результат транскрипции получен, сохраняет его в базе данных.
    - Если результат сохранен, изменяет статус транскрибации звонка в базе данных.
    """
    logger.info("[+] Start transcribe handler")
    db_call = CallData()
    db_analysis = AnalysisData()
    await db_analysis.create_tables()
    while True:
        try:
            calls_for_transcription = await db_call.get_calls_for_transcription()
            if not calls_for_transcription:
                logger.info("[PAUSE] calls_for_transcription is empty, transcribe_handler sleep 5min")
                await asyncio.sleep(300)
                continue
            for call in calls_for_transcription:
                filename = call["file_name"]
                transcription_result = await get_transcription_whisper(filename=filename)
                if transcription_result is not None:
                    rec_result = await db_analysis.set_transcription(call["call_id"], transcription_result)
                    if rec_result:
                        await db_call.update_status(call["call_id"], "TRANSCRIBE_STATUS", "[+]")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}")


if __name__ == "__main__":
    asyncio.run(main())
