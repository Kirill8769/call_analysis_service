import os

import whisper

from config import PATH_PROJECT
from loggers import logger


async def get_transcription_whisper(filename: str) -> dict | None:
    """
    Функция принимает имя аудиофайла в качестве параметра и возвращает результат транскрипции
    файла с помощью библиотеки Whisper.

    :param filename: Имя аудио файла.
    :return: Полученный из аудио файла словарь с текстом и расшифровкой каналов
    """
    transcription_result = None
    model = "large"
    try:
        if not isinstance(filename, str):
            raise TypeError("Передан неверный filename, ожидается тип данных str")
        input_file = os.path.join(PATH_PROJECT, "audio", filename)
        if not os.path.isfile(input_file):
            raise FileNotFoundError("Аудиофайл не найден, проверьте передаваемый путь")
        setting_model = whisper.load_model(model)
        logger.info(f"[+] Началась обработка звонка {filename}")
        transcription_result = setting_model.transcribe(input_file, language="ru", fp16=False)
    except TypeError as type_ex:
        logger.error(f"{type_ex.__class__.__name__}: {type_ex}")
    except FileNotFoundError as file_ex:
        logger.error(f"{file_ex.__class__.__name__}: {file_ex}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    else:
        logger.info(f"[+] Успешно завершилась обработка звонка {filename}")
    finally:
        return transcription_result
