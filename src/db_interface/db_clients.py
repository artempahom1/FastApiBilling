import asyncio

from datetime import datetime, timedelta
from os.path import exists
from typing import Sequence


from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


import db_interface.db_models as db_models



class AsyncPostgreClient:
    '''Клиент Postgres для выполнения асинхронных операций с БД'''

    async def set_domain(
            self,
            session:AsyncSession,
            domain_name: str,
            preferred_timeout: int
    ) -> None:
        '''
        Функция установки домена в таблице биллинга
        :param: sesssion: асинхронная сессия БД
        :param: domain_name: имя домена
        :param: preferred_timeout: размер задержки между запросами к домену в сек
        :return: None
        '''
        new_domain = db_models.Billing(
            domain=domain_name,
            preferred_timeout=preferred_timeout,
            last_query_datetime=None
        )
        query = select(db_models.Billing).where(
            db_models.Billing.domain == domain_name
        )
        search_res = await session.execute(query)
        exists = search_res.scalars().all()
        print(f'EXISTS VAL = {exists}')
        if exists:
            print('EXISTS')
            print(f'LAST QUERY DATETIME = {exists[0].last_query_datetime}')
            query = update(db_models.Billing).where(
                db_models.Billing.domain == domain_name
            ).values(
                preferred_timeout=preferred_timeout,
                last_query_datetime = exists[0].last_query_datetime
            )
            await session.execute(query)
        else:
            print('NOT EXISTS')
            session.add(new_domain)

    async def get_domain(
            self,
            session:AsyncSession,
            domain_name: str
    ) -> Sequence[db_models.Billing]:
        '''
        Функция получения записи домена из таблицы биллинга
        :param: sesssion: асинхронная сессия БД
        :param: domain_name: имя домена
        :return: Sequence: записи из таблицы биллинга по домену
        '''
        query = select(db_models.Billing).where(
            db_models.Billing.domain == domain_name
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def update_domain_timing(
            self,
            session:AsyncSession,
            domain_name: str,
            new_timing: datetime
    ) -> None:
        '''
        Функция обновления таймера для записи домена в таблице биллинга
        :param: sesssion: асинхронная сессия БД
        :param: domain_name: имя домена
        :param: new_timing: новое значение таймера
        :return: None
        '''
        query = update(db_models.Billing).where(
            db_models.Billing.domain == domain_name
        ).values()
        await session.execute(query)

    async def delete_domain(
            self,
            session: AsyncSession,
            domain_name: str
    ) -> None:
        query = delete(db_models.Billing).where(
            db_models.Billing.domain == domain_name
        )
        await session.execute(query)

