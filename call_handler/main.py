import asyncio

from call_handler.rest_bitrix_get import BitrixGet
from call_handler.rest_bitrix_post import BitrixPost
from config import LISTEN_USERS, USER_DATE
from db.db_call_data import CallData
from db.db_user_data import UserData
from db.db_utils import GeneralDB
from loggers import logger


async def main() -> None:
    """
    Основная функция для обработки данных из Bitrix24 и их сохранения в базе данных.

    Создает экземпляры классов BitrixAPI и BitrixData, устанавливает соединение с базой данных,
    запускает метод создания таблиц.
    Обновляет данные опрашиваемых сотрудников
    В цикле:
    - Проверяет и передаёт новые данные в Битрикс24
    - Получает информацию о звонках из Битрикс24, фильтрует их, и сохраняет в базу данных.
    """
    logger.info("[+] Start call handler")
    bitrix_get = BitrixGet()
    bitrix_post = BitrixPost()
    call_db = CallData()
    general_db = GeneralDB()
    user_db = UserData()
    await call_db.create_tables()

    tmp_start_date = await call_db.get_start_date()
    if not tmp_start_date:
        tmp_start_date = USER_DATE
    tmp_start_date = USER_DATE

    db_users_id = await user_db.get_users_id()
    for user_id in LISTEN_USERS:
        user_info = bitrix_get.get_user_data(user_id)
        if user_info is not None:
            if user_info[0]["ID"] in db_users_id:
                await user_db.update_user(user_info[0])
            else:
                await user_db.insert_user(user_info[0])

    while True:
        try:
            transfer_list_to_bitrix = await general_db.get_calls_data_for_send_bitrix()
            if transfer_list_to_bitrix:
                for data in transfer_list_to_bitrix:
                    status_result = bitrix_post.post_element(call_analysis_info=data)
                    if status_result is not None:
                        await call_db.update_status(data["call_id"], "SEND_STATUS", "[+]")

            last_calls_id = await call_db.get_id_calls()
            response_call = bitrix_get.get_call_list(start_date=tmp_start_date)
            if response_call is None:
                raise ValueError("Не был получен список с информацией по звонкам")
            for count, call in enumerate(response_call, start=1):
                if (
                    call["ID"] not in last_calls_id
                    and call["RECORD_FILE_ID"]
                    and call["PORTAL_USER_ID"] in LISTEN_USERS
                    and call["CRM_ENTITY_TYPE"] in ("LEAD", "CONTACT", "COMPANY")
                ):
                    deal_id = bitrix_get.get_deal_id(call["CRM_ENTITY_TYPE"], call["CRM_ENTITY_ID"])
                    deal_stage = bitrix_get.get_deal_stage(deal_id=deal_id) if deal_id else None
                    file_name = bitrix_get.get_filename(call["RECORD_FILE_ID"])
                    user_data = await user_db.get_user_info(int(call["PORTAL_USER_ID"]))
                    user_fio = f'{user_data["last_name"]} {user_data["first_name"]}' if user_data else None
                    await call_db.insert_data(call=call,
                                              portal_user_name=user_fio,
                                              deal_id=deal_id,
                                              file_name=file_name,
                                              deal_stage=deal_stage)
        except ValueError as val_ex:
            logger.warning(f"{val_ex.__class__.__name__}: {val_ex}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            tmp_start_date = response_call[-1]["CALL_START_DATE"]
        finally:
            logger.info("PAUSE: call_handler sleep 5min")
            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
