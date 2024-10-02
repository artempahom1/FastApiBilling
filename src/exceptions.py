from fastapi import HTTPException


class DuplicatedEntryError(HTTPException):
    '''Дубликат primary key в БД'''
    def __init__(self, message: str):
        super().__init__(status_code=422, detail=message)