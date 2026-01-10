class ProactiveManagerError(Exception):
    """Base exception class for Proactive Manager."""
    pass

class ServiceError(ProactiveManagerError):
    """Raised when a service logic fails."""
    pass

class AuthError(ServiceError):
    """Raised when authentication fails."""
    pass

class SlackIntegrationError(ServiceError):
    """Raised when Slack API interaction fails."""
    pass

class CalendarSyncError(ServiceError):
    """Raised when Calendar synchronization fails."""
    pass
