import asyncio


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import URL


import db_interface.db_models as db_models


class BaseConnection:
    def __init__(self, host: str, port: int, db_name: str, login:str, password:str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.login = login
        self._password = password

    def init_all_models(self) -> None:
        pass

    def init_model(self, db_model: object) -> None:
        pass

    def get_session(self) -> None:
        pass


class AsyncBaseConnection(BaseConnection):
    def __init__(self, host: str, port: int, db_name: str, login: str, password: str):
        super().__init__(host, port, db_name, login, password)

    async def init_all_models(self) -> None:
        pass

    async def init_model(self, db_model: object) -> None:
        pass

    async def get_session(self) -> None:
        pass

class PostgreAsyncDbConnection(AsyncBaseConnection):
    def __init__(self, host: str, port: int, db_name: str, login:str, password:str):
        super().__init__(host, port, db_name, login, password)
        url_object = URL.create(
            'postgresql+asyncpg',
            username=self.login,
            password=self._password,
            host=self.host,
            port=self.port,
            database=self.db_name
        )
        self.engine = create_async_engine(
            url_object,
            echo=True,
            execution_options={
                "isolation_level": "SERIALIZABLE"
            }
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession
        )
        print('initializing_tables')
        self.init_all_models()
        print('finished initializing_tables')

    async def init_all_models(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(db_models.BaseModel.metadata.create_all)

    async def init_model(self, db_model: db_models.BaseModel) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(db_model.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        async with self.async_session() as session:
            yield session
