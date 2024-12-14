from .base import Base
from copy import deepcopy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, delete, and_
from os import getenv
from loguru import logger
from ..migrations.vacancies.models import VacanciesModel

class VacanciesActions(Base):
    def __init__(self):
        super().__init__()
        self.db = None

    async def __aenter__(self):
        vacancies_db_string_conection = getenv('VACANCIES_DB_STRING_CONNECTION')
        if vacancies_db_string_conection:
            self.db = Session(
                create_engine(
                    vacancies_db_string_conection,
                    echo=False,
                    connect_args={
                        'check_same_thread': False
                    }
                )
            )

        return self
    
    def __delete_all_vacancies(self) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            db.query(VacanciesModel).delete()
            db.commit()

            response_json['status'] = 'success'

        except (SQLAlchemyError, Exception, ) as e:
            response_json['err_description'] = str(e)
            if db:
                db.rollback()

        finally:
            return response_json
    
    def __delete_vacancy(self, vacancy_id: int) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            stmt = delete(VacanciesModel).where(VacanciesModel.id == vacancy_id)
            db.execute(stmt)
            db.commit()

            response_json['status'] = 'success'

        except (SQLAlchemyError, Exception, ) as e:
            response_json['err_description'] = str(e)
            if db:
                db.rollback()

        finally:
            return response_json
        
    def __select_all_vacancies(self, page: int = 1) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            stmt = select(VacanciesModel)
            if page:
                per_page = 12
                offset = (page - 1) * per_page 
                stmt.offset(offset).limit(per_page)
            
            vacancies = []
            for row in db.scalars(stmt):
                vacancies.append(
                    row.to_json()
                )

            response_json['vacancies'] = vacancies
            response_json['status'] = 'success'

        except (SQLAlchemyError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    def __select_vacancy(self, db: Session, **kwargs) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            vacancy_id, vacancy_title = kwargs.get('vacancy_id', None), kwargs.get('vacancy_title', None)
            if not any((vacancy_id, vacancy_title)):
                raise ValueError('Недостатньо даних для виконання запиту!')

            stmt = select(VacanciesModel)
            if vacancy_id and not vacancy_title:
                stmt = stmt.where(VacanciesModel.id == vacancy_id)
            elif vacancy_title and not vacancy_id:
                stmt = stmt.where(VacanciesModel.title == vacancy_title)
            elif vacancy_id and vacancy_title:
                stmt = stmt.where(
                    and_(VacanciesModel.id == vacancy_id, VacanciesModel.title == vacancy_title)
                )

            vacancy = db.scalars(stmt).first()
            response_json['vacancy'] = vacancy.to_json() if vacancy else {}
            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)
        
        finally:
            return response_json
    
    def __add_vacancy(self, title: str, description: str) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            select_vacancy_response = self.__select_vacancy(db, vacancy_title=title)

            exists_vacancy = select_vacancy_response.get('vacancy', {})
            logger.info(exists_vacancy)

            if exists_vacancy:
                db.query(VacanciesModel).filter(VacanciesModel.title == title).update({
                    VacanciesModel.description: description
                })
            
            else:
                new_vacancy = VacanciesModel(
                    title=title,
                    description=description
                )
                logger.info(new_vacancy)

                db.add(new_vacancy)
            
            db.commit()

            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)
            if db:
                db.rollback()

        finally:
            return response_json
    
    async def _executing_process(self, *args, **kwargs) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            action = kwargs.get('action')
            
            if not action:
                raise ValueError('Виконнання цього запиту неможливе.')
            
            if action == 'add_vacancy':
                if len(args) != 2:
                    raise ValueError('Некоректна кількість необхідних параметрів для виконання запиту.')
                
                title, description, *_ = args
                add_vacancy_response = self.__add_vacancy(
                    title, description,
                )

                if add_vacancy_response.get('status', 'error') == 'error':
                    raise Exception(
                        add_vacancy_response.get('err_description', '')
                    )
            
            elif action == 'select_all_vacancies':
                if len(args) != 1:
                    raise ValueError('Некоректна кількість необхідних параметрів для виконання запиту.')
                
                page, *_ = args
                select_all_vacancies_response = self.__select_all_vacancies(
                    page
                )

                if select_all_vacancies_response.get('status', 'error') == 'error':
                    raise Exception(
                        select_all_vacancies_response.get('err_description', '')
                    )
                
                response_json['vacancies'] = select_all_vacancies_response.get('vacancies', [])

            elif action == 'delete_all_vacancies':
                delete_all_vacancies_response = self.__delete_all_vacancies(
                    
                )

                if delete_all_vacancies_response.get('status', 'error') == 'error':
                    raise Exception(
                        delete_all_vacancies_response.get('err_description', '')
                    )
            
            elif action == 'delete_vacancy':
                if len(args) != 1:
                    raise ValueError('Некоректна кількість необхідних параметрів для виконання запиту.')
                
                vacancy_id, *_ = args
                delete_vacancy_response = self.__delete_vacancy(
                    vacancy_id
                )

                if delete_vacancy_response.get('status', 'error') == 'error':
                    raise Exception(
                        delete_vacancy_response.get('err_description', '')
                    )
                
            else: 
                raise Exception('Виконання запиту завершилося невдало.')

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def add_vacancy(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            title, description = data.get('title', ''), data.get('description', '')
            if not all((title, description)):
                raise ValueError('Некоректна кількість необхідних параметрів для виконання запиту.')
            
            executing_process_response = await self._executing_process(
                title, description,
                action='add_vacancy'
            )

            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def select_all_vacancies(self, page: int = 1) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(
                page,
                action='select_all_vacancies'
            )

            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['items'] = executing_process_response.get('vacancies', [])
            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def delete_vacancy(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            vacancy_id = data.get('vacancy_id', '')
            if not vacancy_id:
                raise ValueError('Некоректна кількість необхідних параметрів для виконання запиту.')

            executing_process_response = await self._executing_process(
                vacancy_id,
                action='delete_vacancy'
            )

            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def delete_all_vacancies(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(
                action='delete_all_vacancies'
            )

            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def __aexit__(self, *args, **kwargs):
        if self.db:
            self.db.close()