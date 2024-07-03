from loggers import logger
from db.db_connector import BaseConnector


class UserData(BaseConnector):
    """Класс для работы с таблицей portal_users."""

    async def get_users_id(self) -> list | list[str]:
        """
        Метод получает список id сотрудников, записанных в таблицу.

        :return: Возвращает список id сотрудников.
        """
        await self.connect()
        db_users_id = []
        try:
            db_users = await self.connection.fetch("SELECT manager_id FROM portal_users")
            db_users_id = [str(user["manager_id"]) for user in db_users]
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return db_users_id

    async def insert_user(self, user: dict) -> None:
        """
        Делает новую запись о сотруднике в БД.

        :param user: Словарь с информацией о сотруднике.
        """
        await self.connect()
        try:
            await self.connection.execute(
                """INSERT INTO portal_users (MANAGER_ID, ACTIVE, FIRST_NAME, LAST_NAME, EMAIL) 
                VALUES ($1, $2, $3, $4, $5)""",
                int(user["ID"]), int(user["ACTIVE"]), user["NAME"], user["LAST_NAME"], user["EMAIL"]
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        else:
            logger.info(f'[+] В БД добавлен новый сотрудник ({user["ID"]}: {user["NAME"]} {user["LAST_NAME"]})')
        finally:
            await self.connection.close()

    async def update_user(self, user: dict) -> None:
        """
        Обновляет запись о сотруднике в БД.

        :param user: Словарь с информацией о сотруднике.
        """
        await self.connect()
        try:
            await self.connection.execute(
                """UPDATE portal_users 
                SET ACTIVE = $1, FIRST_NAME = $2, LAST_NAME = $3, EMAIL = $4, REGION = $5
                WHERE MANAGER_ID = $6""",
                int(user["ACTIVE"]), user["NAME"], user["LAST_NAME"], user["EMAIL"], None, int(user["ID"])
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()

    async def get_user_info(self, manager_id: int) -> dict:
        """
        Метод получает информацию о сотруднике из базы данных.

        :param manager_id: ID сотрудника.
        :return: Возвращает словарь с информацией.
        """
        await self.connect()
        user_info = dict()
        try:
            user_info = dict(
                await self.connection.fetchrow("SELECT * FROM portal_users WHERE MANAGER_ID = $1", manager_id)
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            await self.connection.close()
            return user_info
