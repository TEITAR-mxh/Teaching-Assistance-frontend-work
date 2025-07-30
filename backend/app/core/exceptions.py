class AppException(Exception):
    """项目通用异常基类"""
    pass

class NotFoundException(AppException):
    pass

class UnauthorizedException(AppException):
    pass

class ValidationException(AppException):
    pass 
