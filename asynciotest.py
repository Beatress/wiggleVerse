import ircsocket
from ircsocket import IrcSocket
import asyncio
import time
def main():
    irc = IrcSocket()

    irc.connect('wiggleland.fun', 6667)
    irc.put_raw('USER cat 8 * :cat')
    irc.put_raw('NICK cat')
    irc.put_raw('JOIN #WiggleWorld')
    while 1:
        line = irc.socket.recv(4096)
        if not line:
            break
        print(line.decode('UTF-8'))

main()