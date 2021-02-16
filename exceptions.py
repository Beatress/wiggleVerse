# Copyright Beatrice Tohni 2021
""" This file is part of wiggleVerse.

    wiggleVerse is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    wiggleVerse is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with wiggleVerse.  If not, see <https://www.gnu.org/licenses/>."""

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