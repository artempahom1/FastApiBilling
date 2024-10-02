# FastApiBilling

## Оглавление
1. [О проекте](#about_project)
2. [Структура проекта](#project_structure)
3. [Запуск](#launch)
4. [Дополнительная информация](#extra_info)


## 1. <a name="about_project">О проекте</a>
Данный репозиторий реализует сервис ограничения кол-ва запросов (биллинга) на определённые домены (вместо домена может быть любой другой идентификатор).
Реализован минимальный набор для работы - GET, POST, DELETE.
Раздел для работы с биллингом - /domain_billing

Ответственный: Востропятов А.И.

## 2. <a name="project_structure">Структура проекта</a>
### /config
Раздел конфигурации сервиса.
### /src
Раздел исполняемого кода.
### /tests
Раздел исполняемого тестов. #todo Добавить unit-тесты
### requirements.txt
Перечень расширений для Python.
### create-db.sql
Скрипт создания БД для PostgreSQL.
### Dockerfile
Файл для сборки Docker образа.
### docker-compose.yaml
Файл для запуска группы сервисов в среде Docker.

## 3. <a name="launch">Запуск</a>
Запуск публикатора сервиса с помощью прямой активации скрипта командой:
```sh
python[VER.] src/billing_service.py
```
или запуском Docker-контейнера из предварительно собранного Docker-образа (сервис в конфиге устанавливать на хост 0.0.0.0):
```sh
docker run -it {имя_образа}
```
или запуском группы сервисов (предпочтительно) из docker-compose (сервис в конфиге устанавливать на хост 0.0.0.0):
```sh
docker-compose up --build -d
```
## 4. <a name="extra_info">Дополнительная информация</a>
Данный проект работает с загрузчиком конфигурации.
Модуль позволяет собирать конфиги из директорий, переменных окружения с помощью классов-моделей данных, инициализирующихся через класс-фабрику. Работает с конфигами типа `json`, `yaml`, `yml`, `ini`, `cfg`.
Для каждой модели приоритет выбора параметра из конфига устанавливаеся отдельно, например, для модели HealthCheckerConfig переменные окружения применяются поверх переменных конфигов.
#### Формат конфига
Конфиги задаются в виде файлов формата config.{расширение}.
Путь к конфигам уточняется через переменную окружения CONFIG_DIR, если переменная не проинициализирована, то используется дефолтный путь в директорию config корня основного проекта ./config.
Подразумевается, что в директории может содержаться только один файл конфигурации, если файлов несколько, то конфиг будет прочитан согласно приоритету: yml -> yaml -> json -> ini -> cfg.

#### Переменные окружения
Для конфигурирования также могут быть использованы переменные окружения.
Предварительно можно определить префикс для имён переменных через переменную окружения SERVICE_NAME, являющуюся именем сервиса, если не указана, то по умолчанию префикс - DataProcessingService.
Имя переменной должно быть задано с учётом следующего формата: `{префикс}_{имя секции (опционально)}__{имя переменной}`, т.е. задавать имена переменных нужно в том числе исходя из структуры конфигурационных файлов, как правило, хранящихся в директории samples корневого проекта.

#### Модель данных
Модель данных представляет собой класс, наследующийся от базового класса `pydantic.BaseSettings`. Поля определяются как статические переменные класса, а источники и порядок их применения к модели определяются в методе customise_sources.
```python
from typing import Optional, Any
from pydantic import BaseSettings, create_model
from pydantic.env_settings import SettingsSourceCallable


class HealthCheckerConfig(BaseSettings):
    """
    Класс модели конфигурации для HealthChecker сервиса
    """
    
    #Поле первого уровня
    first_lvl_field: str
    
    #Поля второго уровня секции options_section
    options_section: create_model('OptionsSection', first_nested_option=(Optional[str], ...),
                                  second_nested_option=(str, ...),
                                  third_nested_option=(int, ...))

    class Config:
        """
        Класс конфигурации модели
        """
        #Определение формата префикса для переменных окружения
        env_prefix = f"PREFIX_"
        #Определение формата разделителя для переменных выше первого уровня
        env_nested_delimiter = '__'

        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """
                Функция добавления источников для модели и установки порядка их применения на модель
                :param: init_settings: Параметры, устанавливаемые при инициализации модели
                :param: env_settings: Параметры, устанавливаемые из среды окружения
                :param: file_secret_settings: Параметры, устанавливаемые из SECRET файла
                :return: tuple: Кортеж источников с приоритезацией (приоритет уменьшается слева направо)
            """
            return init_settings, env_settings, read_config_setting
```

#### Чтение конфига
```python
from dp_python_helper.config_module.configuration import GenericConfig, create_model
from typing import Optional
#Создаём класс, наследующий класс GenericConfig, в нём определяем поля, изменяем поведение
class CheckerConfig(GenericConfig):
    checker_options: create_model('CheckerOptions', pid_file=(Optional[str], ...),
                                  err_log_file=(str, ...),
                                  out_log_file=(str, ...),
                                  home_dir=(Optional[str], ...),
                                  expire_timeout=(str, ...),
                                  time_delta=(str, ...),
                                  daemonize=(Optional[str], ...),
                                  collection_name=(str, ...))
    database_options: create_model('DatabaseOptions', dbname=(str, ...),
                                   dbschema=(str, ...),
                                   dbtable=(str, ...),
                                   dbuser=(Optional[str], ...),
                                   dbhost=(str, ...),
                                   dbport=(str, ...),
                                   dbpassword=(Optional[str], ...))
    slack_options: create_model('SlackOptions', url=(str, ...),
                                interval=(str, ...),
                                username=(str, ...))
    mail_options: create_model('MailOptions', interval=(str, ...),
                               recipients=(str, ...),
                               port=(str, ...),
                               server=(str, ...),
                               sender=(str, ...))

#Чтение конфигурации из источников по заданной модели
config = CheckerConfig()
```

#### Получение данных
Пусть у нас имеется конфиг `config.yml`

```yaml
first_lvl_field: 123
options_section: 
    first_nested_option: hello
    second_nested_option: world
    third_nested_option: 12
```

```python
config.first_lvl_field
# 123

config.options_section
# OptionSection(...)

config.options_section.first_nested_option
# hello
```


