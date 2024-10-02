import asyncio

from typing import Annotated


import uvicorn

from fastapi import FastAPI

from fastapi import Depends

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError

from contextlib import asynccontextmanager


from exceptions import DuplicatedEntryError

from db_interface.db_connections import PostgreAsyncDbConnection

from db_interface.db_clients import AsyncPostgreClient

from models import SetBody

from config.config_loader import GenericConfig, create_model


class BillingServiceConfig(GenericConfig):
    '''Класс конфигурации сервиса биллинга'''
    service_run_options: create_model('ServiceRunOptions',
                             host=(str, ...),
                             port=(int, ...))
    db_options: create_model('DBOptions',
                                 host=(str, ...),
                                 port=(int, ...),
                                 db_name=(str, ...),
                                 user=(str, ...),
                                 password=(str, ...))
    logger_options: create_model('LoggerOptions',
                                 logs_level=(str, ...))

    class Config:
        extra = 'ignore'


billing_config = BillingServiceConfig()

db_connection = PostgreAsyncDbConnection(
    billing_config.db_options.host,
    billing_config.db_options.port,
    billing_config.db_options.db_name,
    billing_config.db_options.user,
    billing_config.db_options.password
)
db_client = AsyncPostgreClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.init_all_models()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/domain_billing')
async def get_status(domain: str, session: AsyncSession = Depends(db_connection.get_session)) -> dict:
    response = await get_billing_db(session, domain)
    return {'status': response}


@app.post('/domain_billing')
async def billing_to_set(body: SetBody, session: AsyncSession = Depends(db_connection.get_session)) -> None:
    await set_billing_db(session, body)

@app.delete('/domain_billing')
async def billing_to_delete(domain: str, session: AsyncSession = Depends(db_connection.get_session)) -> dict:
    res = await delete_billing_db(session, domain)
    return res


async def set_billing_db(session: AsyncSession, body: SetBody) -> None:
    '''
    Функция установки биллинга для домена
    :param: sesssion: асинхронная сессия БД
    :param: body: тело запроса POST
    :return: None
    '''
    await db_client.set_domain(session, body.domain, body.timeout_value)
    try:
        await session.commit()
        return body
    except IntegrityError as ex:
        await session.rollback()
        raise DuplicatedEntryError('Same row already exists')


async def get_billing_db(session: AsyncSession, domain: str):
    '''
    Функция получения разрешения на обращение к домену
    :param: sesssion: асинхронная сессия БД
    :param: domain: имя домена
    :return: dict: разрешение на проведение операции на домене
    '''
    result = await db_client.get_domain(session, domain)
    if not result:
        return {'permission': True}
    elif not result[0].last_query_datetime:
        print('NONE')
        await db_client.update_domain_timing(session, domain, datetime.utcnow())
        await session.commit()
        return {'permission': True}
    else:
        print('DATETIME')
        print(result[0].last_query_datetime)
        print('TIMEOUT')
        print(result[0].preferred_timeout)
        if datetime.utcnow() - result[0].last_query_datetime >= timedelta(
                seconds=result[0].preferred_timeout):
            await db_client.update_domain_timing(session, domain, datetime.utcnow())
            await session.commit()
            return {'permission': True}
        else:
            return {'permission': False}

async def delete_billing_db(session: AsyncSession, domain: str):
    '''
    Функция удаления домена из биллинга
    :param: sesssion: асинхронная сессия БД
    :param: domain: имя домена
    :return: dict: информация об удалённом домене
    '''
    await db_client.delete_domain(session, domain)
    await session.commit()
    return {'deleted': domain}


if __name__ == '__main__':
    uvicorn.run(
        app,
        host=billing_config.service_run_options.host,
        port=billing_config.service_run_options.port
    )