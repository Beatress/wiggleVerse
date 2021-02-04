class SocketAlreadyConnected(OSError):
    def __init__(self, message='A duplicate connection attempt was made', errors=None):
        super().__init__(message, errors)

class SocketTimeout(OSError):
    def __init__(self, message='Connection failed: Socket timed out', errors=None):
        super().__init__(message, errors)

class SocketNotConnected(OSError):
    def __init__(self, message='You attempted to send/receive data, but socket isn\'t connected', errors=None):
        super().__init__(message, errors)

class SocketConnectionBroken(OSError):
    def __init__(self, message='The socket connection broke unexpectedly', errors=None):
        super().__init__(message, errors)