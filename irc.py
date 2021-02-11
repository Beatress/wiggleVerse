import socket
import ircsocket
import threading
import logging
from ircsocket import IrcSocket
from exceptions import *

class Irc:
    """A class to manage channels and users on one IRC network
    This class is a wrapper for the IrcSocket class
    """
    def get_messages(self, stop, buffer):
        while 1:
            if stop:
                logging.info('[IRC] Receive thread sent stop signal')
                break
            try:
                lines = self.socket.get_raw()
                for line in lines:
                    # Handle ping and pong here
                    if line[0:4] == 'PING':
                        self.send_raw('PONG' + line[4:])
                        logging.debug('Sent pong successfully')
                        continue
                    buffer.put(line)
            except OSError as err:
                logging.error(err)
                if self.connected:
                    self.buffer.put(f'>>Error receiving messages: {err}')
                    self.disconnect()
                logging.info('[IRC] Socket error in receive thread, stopping...')
                break
            
    def __init__(self, host, port, nick, user, real, get_messages_callback, buffer, tag=False):
        """Create a new IRC instance
        Each instance represents one connection to one server"""
        self.host = host
        self.port = port
        self.nick = nick
        self.user = user
        self.real = real
        self.channels = []
        self.get_messages_callback = get_messages_callback
        self.buffer = buffer
        self.connected = False

        # Assign server tag if none given
        # This works well for host names, is not great for IPs but oh well
        if not tag:
            try:
                self.tag = host.split('.')[:-2]
            except IndexError:
                self.tag = host
        
    def connect(self):
        # Try to connect
        if self.connected:
            buffer.put('>>We are already connected')
        try:
            self.socket = IrcSocket()
            self.socket.connect(self.host, self.port)
            self.socket.put_raw(f"USER {self.user} 0 * :{self.real}")
            # TODO Support alternate nick
            self.socket.put_raw(f"NICK {self.nick}")
            self.stop_thread = False # used to stop the thread when connection dies
            self.receive_thread = threading.Thread(target=self.get_messages, args=(self.stop_thread, self.buffer,), daemon=True)
            self.receive_thread.start()
            self.connected = True

        except OSError as err:
            logging.error(err)
            self.buffer.put(f'>>Connection failed due to error: {err}')
            self.disconnect()

    def disconnect(self):
        """Shut down the socket and run clean up code"""
        try:
            logging.debug('[IRC] Disconnection process started')
            self.connected = False
            self.stop_thread = True # failsafe
            self.socket.disconnect()
        except OSError as err:
            logging.warning('[IRC] IRC socket reported error closing.')
        finally:
            logging.info('[IRC] IRC connection closed')
            logging.debug('[IRC] Disconnection process finished')
            self.buffer.put('>>IRC connection lost')
            self.buffer.put('[wiggleVerse] DROPCON')

    def send_raw(self, message):
        try:
            self.socket.put_raw(message)
        except OSError as err:
            logging.error(f"[IRC] Error sending: {err}")
            buffer.put(f'>>Error sending message: {err}')
            buffer.put('Disconnecting...')
            self.disconnect()

    def is_connected(self):
        return self.connected

    def get_tag(self):
        return self.tag

    # def join(self, channel):
    #     pass

    # def part(self, channel):
    #     pass

    # def nick(self, new_nick):
    #     pass
