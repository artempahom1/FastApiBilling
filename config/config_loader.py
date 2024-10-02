import yaml
import json
import os
from configparser import ConfigParser
from typing import Any, Type
from pydantic_settings import BaseSettings
from pydantic import create_model
from pydantic_settings import PydanticBaseSettingsSource


class ConfigReaderError(Exception):
    pass


class MyParser(ConfigParser):
    '''
    Класс-обертка с функционалом преобразования объекта ConfigParser в словарь dict()
    '''
    def as_dict(self):
        '''
        Функция преобразования в словарь dict
        :return: d: dict Представление объекта ConfigParser в виде словаря
        '''
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


class GenericConfig(BaseSettings):
    '''
    Класс модели конфигурации сервиса
    '''

    class Config:
        '''
        Класс конфигурации модели
        '''
        if not os.getenv('SERVICE_NAME'):
            service_name = 'DataProcessingService'
        else:
            service_name = os.getenv('SERVICE_NAME')
        env_prefix = f'{service_name}_'
        env_nested_delimiter = '__'

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ):
        '''
            Функция добавления источников для модели и установки порядка их применения на модель
            :param: settings_cls: Класс настроек
            :param: init_settings: Параметры, устанавливаемые при инициализации модели
            :param: env_settings: Параметры, устанавливаемые из среды окружения
            :param: dotenv_settings: Параметры, устанавливаемые из .env файлов
            :param: file_secret_settings: Параметры, устанавливаемые из SECRET файла
            :return: tuple: Кортеж источников с приоритезацией (приоритет уменьшается слева направо)
        '''
        return init_settings, env_settings, read_config_setting


def read_config_setting():
    '''
    Функция чтения конфигурационных файлов
    :param: settings: Настройки pydantic
    :return: dict: Словарь с конфигурацией
    '''
    if os.getenv('CONFIG_DIR'):
        config_dir = os.getenv('CONFIG_DIR')
    else:
        config_dir = './config'
    if os.path.exists(os.path.join(config_dir, 'config.yml')):
        with open(os.path.join(config_dir, 'config.yml')) as conf_file:
            return yaml.safe_load(conf_file)
    elif os.path.exists(os.path.join(config_dir, 'config.yaml')):
        with open(os.path.join(config_dir, 'config.yaml')) as conf_file:
            return yaml.safe_load(conf_file)
    elif os.path.exists(os.path.join(config_dir, 'config.json')):
        with open(os.path.join(config_dir, 'config.json')) as conf_file:
            return json.load(conf_file)
    elif os.path.exists(os.path.join(config_dir, 'config.ini')):
        config = MyParser()
        config.read(os.path.join(config_dir, 'config.ini'))
        return config.as_dict()
    elif os.path.exists(os.path.join(config_dir, 'config.cfg')):
        config = MyParser()
        config.read(os.path.join(config_dir, 'config.cfg'))
        return config.as_dict()
    else:
        return dict()
