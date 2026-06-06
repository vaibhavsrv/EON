"""
Custom exceptions for EON AI Brain
"""


class EONException(Exception):
    """Base exception for all EON errors"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ValidationError(EONException):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class ToolNotFoundError(EONException):
    """Raised when requested tool doesn't exist"""
    def __init__(self, tool_name: str):
        super().__init__(
            f"Tool '{tool_name}' not found",
            "TOOL_NOT_FOUND",
            {"tool": tool_name}
        )


class ParameterMissingError(EONException):
    """Raised when required parameter is missing"""
    def __init__(self, parameter: str, tool: str):
        super().__init__(
            f"Missing required parameter '{parameter}' for tool '{tool}'",
            "PARAMETER_MISSING",
            {"parameter": parameter, "tool": tool}
        )


class ParameterTypeError(EONException):
    """Raised when parameter has wrong type"""
    def __init__(self, parameter: str, expected_type: str, got_type: str):
        super().__init__(
            f"Parameter '{parameter}' should be {expected_type}, got {got_type}",
            "PARAMETER_TYPE_ERROR",
            {"parameter": parameter, "expected": expected_type, "got": got_type}
        )


class LLMError(EONException):
    """Raised when LLM call fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "LLM_ERROR", details)


class SessionError(EONException):
    """Raised when session management fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "SESSION_ERROR", details)


class MemoryError(EONException):
    """Raised when memory operation fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "MEMORY_ERROR", details)


class IntentError(EONException):
    """Raised when intent parsing fails"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "INTENT_ERROR", details)
