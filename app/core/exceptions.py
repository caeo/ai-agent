class AIServiceUnavailableError(Exception):
    """Indica que não foi possível acessar o serviço de IA."""


class AIServiceTimeoutError(Exception):
    """O serviço de IA excedeu o tempo de espera"""
