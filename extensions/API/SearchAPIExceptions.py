from typing import NoReturn, Type


class ExceptionIsImutable(Exception):
    @property
    def attempt_e(self):
        return self.__attempt_e

    @property
    def attempt_var(self):
        return self.__attempt_var

    @property
    def new_value(self):
        return self.__new_value

    def __init__(self, attempt_e: Exception, attempt_var: str, new_value):
        self.__attempt_e = attempt_e
        self.__attempt_var = attempt_var
        self.__new_value = new_value

    @classmethod
    def property_immutable(cls, *args, **kwargs):
        raise ExceptionIsImutable(*args, **kwargs)


class SearchAPIException(Exception):
    @property
    def query(self) -> str:
        return self.__query

    @query.setter
    def query(self, value) -> NoReturn:
        ExceptionIsImutable.property_immutable(attempt_e=self, attempted_var="query", new_value=value)

    @property
    def api(self) -> str:
        return self.__api

    @api.setter
    def api(self, value) -> NoReturn:
        ExceptionIsImutable.property_immutable(attempt_e=self, attempted_var="api", new_value=value)

    @property
    def exception(self) -> Type[Exception]:
        return self.__exception

    @exception.setter
    def exception(self, value) -> NoReturn:
        ExceptionIsImutable.property_immutable(attempt_e=self, attempted_var="exception", new_value=value)

    def __init__(self, api: str, query: str, exception: Type[Exception], *args, **kwargs):
        super().__init__(args, kwargs)
        self.__api: str = api
        self.__query: str = query
        self.__exception: Type[Exception] = exception


class NaverSearchException(SearchAPIException):
    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value):
        ExceptionIsImutable.property_immutable(attempt_e=self, attempted_var="category", new_value=value)

    @property
    def response_format(self):
        return self.__response_format

    @response_format.setter
    def response_format(self, value):
        ExceptionIsImutable.property_immutable(attempt_e=self, attempted_var="response_format", new_value=value)

    def __init__(self, category, response_format, query, *args, **kwargs):
        super().__init__(api="naver", query=query, exception=self, *args, **kwargs)
        self.__category = category
        self.__response_format = response_format

    def __str__(self) -> str:
        return "[ Naver Search API ] An exception occured during parsing the search result!"

    def get_request_info(self):
        return f"[ category : {self.response_format} | requested response format : {self.response_format} | query : {self.query}"


class NaverSearch_CategoryNotSupported(NaverSearchException):
    def __str__(self) -> str:
        return f"[ Naver Search API ] Category {self.category} is not supported."


class NaverSearch_ResponseFormatNotSupported(NaverSearchException):
    def __str__(self) -> str:
        return f"[ Naver Search API ] Response format {self.response_format} is not supported {self.category} category."
