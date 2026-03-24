class SimLLMGameError(Exception):
    pass


class ValidationError(SimLLMGameError):
    pass


class MemoryConflictError(SimLLMGameError):
    pass
