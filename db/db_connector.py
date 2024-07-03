import os

import asyncpg
from dotenv import load_dotenv

from loggers import logger


class BaseConnector:
    """Подключает к базе данных и создаёт таблицы."""

    def __init__(self) -> None:
        self.connection = None
        load_dotenv()
        self.database = os.getenv("POSTGRES_DB")
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.host = os.getenv("POSTGRES_HOST")
        self.port = os.getenv("POSTGRES_PORT")
        logger.info("Database is activated")

    async def connect(self) -> None:
        """Устанавливает соединение с базой данных."""

        try:
            self.connection = await asyncpg.connect(
                host=self.host, port=self.port, database=self.database, user=self.user, password=self.password
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    async def create_tables(self) -> None:
        """Создает таблицу в базе данных, если она не существует."""

        await self.connect()
        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS portal_users(
                ID SERIAL PRIMARY KEY,
                MANAGER_ID INT UNIQUE,
                ACTIVE INT,
                FIRST_NAME VARCHAR(64),
                LAST_NAME VARCHAR(64),
                EMAIL VARCHAR(128),
                REGION VARCHAR(64)
            )
            """
        )

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS b24_calls(
                ID SERIAL PRIMARY KEY,
                CALL_ID VARCHAR(32) UNIQUE NOT NULL,
                STAGE VARCHAR(64),
                MANAGER_ID INT NOT NULL,
                PORTAL_USER_NAME VARCHAR(256),
                RECORD_FILE_ID INT,
                TYPE VARCHAR(64),
                DATE VARCHAR(64),
                TIMEZONE VARCHAR(64),
                DURATION INT,
                DURATION_VISUAL VARCHAR(64),
                DEAL_ID VARCHAR(32),
                CRM_ENTITY_TYPE VARCHAR(32),
                CRM_ENTITY_ID VARCHAR(32),
                CRM_ACTIVITY_ID VARCHAR(32),
                PORTAL_NUMBER VARCHAR(64),
                PHONE_NUMBER VARCHAR(64),
                DEAL_URL VARCHAR(512),
                FILE_URL VARCHAR(512),
                FILE_NAME VARCHAR(256),
                SEND_STATUS VARCHAR(32),
                TRANSCRIBE_STATUS VARCHAR(32),
                ANALYSIS_STATUS VARCHAR(32),              
                FOREIGN KEY (MANAGER_ID) REFERENCES portal_users (MANAGER_ID)
            )
            """
        )

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS call_analysis(
                ID SERIAL PRIMARY KEY,
                CALL_ID VARCHAR(32),
                TRANSCRIBE_CALL TEXT,
                SEGMENTS JSONB,    
                GENERAL_COMMENT TEXT,
                CALL_QUALITY NUMERIC(4, 1),             
                RESUME_MANAGER TEXT,
                RECOMMENDATIONS TEXT,
                FOREIGN KEY (CALL_ID) REFERENCES b24_calls (CALL_ID)
            )
            """
        )

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations(
                ID SERIAL PRIMARY KEY,
                CALL_ID VARCHAR(32),
                GREETING INT,
                SPEECH INT,
                INITIATIVE INT,
                NEED INT,
                OFFER INT,
                OBJECTION INT,
                PERSEVERANCE INT,
                ADVANTAGES INT,
                AGREEMENT INT,
                FOREIGN KEY (CALL_ID) REFERENCES b24_calls (CALL_ID)       
            )
            """
        )

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS commentary(
                ID SERIAL PRIMARY KEY,
                CALL_ID VARCHAR(32),
                GREETING VARCHAR(1024),
                SPEECH VARCHAR(1024),
                INITIATIVE VARCHAR(1024),
                NEED VARCHAR(1024),
                OFFER VARCHAR(1024),
                OBJECTION VARCHAR(1024),
                PERSEVERANCE VARCHAR(1024),
                ADVANTAGES VARCHAR(1024),
                AGREEMENT VARCHAR(1024),
                FOREIGN KEY (CALL_ID) REFERENCES b24_calls (CALL_ID)
            )
            """
        )
        await self.connection.close()
