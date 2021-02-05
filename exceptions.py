class SocketAlreadyConnected(OSError):
    def __init__(self, message='A duplicate connection attempt was made'):
        super().__init__(message)

class SocketTimeout(OSError):
    def __init__(self, message='Connection failed: Socket timed out'):
        super().__init__(message)

class SocketNotConnected(OSError):
    def __init__(self, message='You attempted to send/receive data, but socket isn\'t connected'):
        super().__init__(message)

class SocketConnectionBroken(OSError):
    def __init__(self, message='The socket connection broke unexpectedly'):
        super().__init__(message)