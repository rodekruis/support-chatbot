class DomainError(Exception):
    """Base class for domain-level errors."""


class AuthenticationError(DomainError):
    """Credentials are missing or invalid."""


class ExternalServiceError(DomainError):
    """An external service failed while processing a request."""
