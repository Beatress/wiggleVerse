import socket
import ircsocket
import threading
import helpers
from ircsocket import IrcSocket
from exceptions import *

class Irc:
    """A class to manage channels and users on one IRC network
    This class is a wrapper for the IrcSocket class
    """
    def get_messages(self):
        while 1:
            try:
                lines = self.socket.get_raw()
                helpers.eprint('got raw data')
                self.get_messages_callback(lines)
            except SocketConnectionBroken:
                helpers.eprint('Connection closed: Socket broke')
                self.socket.disconnect()
            except OSError as err:
                helpers.eprint(err)     
            
    def __init__(self, host, port, nick, user, real, get_messages_callback, tag=False):
        """Create a new IRC instance
        Each instance represents one connection to one server"""
        # Assign server tag if none given
        # This works well for host names, is not great for IPs but oh well
        if not tag:
            try:
                self.tag = host.split('.')[:-2]
            except IndexError:
                self.tag = host

        self.socket = IrcSocket()
        self.nick = nick
        self.get_messages_callback = get_messages_callback
        self.connected = False
        # anything else needed to save
        # 
        # Try to connect
        try:
            self.socket.connect(host, port)
            self.socket.put_raw(f"USER {user} 0 * :{real}")
            # TODO Support alternate nick
            self.socket.put_raw(f"NICK {nick}")
            # self.socket.put_raw('JOIN #test') # TODO remove
            self.receive_thread = threading.Thread(target=self.get_messages, daemon=True)
            self.receive_thread.start()
            self.connected = True

        except OSError as err:
            helpers.eprint(err)
        # TODO handle failures better

    def disconnect(self):
        """Shut down the socket and run clean up code"""
        try:
            self.connected = False
            self.socket.disconnect()
        except OSError as err:
            helpers.eprint('IRC socket reported error closing.')
        finally:
            # clean up code goes here
            helpers.eprint('IRC connection lost')
            pass

    def send_raw(self, message):
        try:
            self.socket.put_raw(message)
        except SocketConnectionBroken:
            helpers.eprint('Connection closed: Socket broke')
            self.socket.disconnect()
        except OSError as err:
            helpers.eprint(err)        


    
