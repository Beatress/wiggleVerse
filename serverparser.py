import re
import logging

class ServerParser:
    def __init__(self, nick, set_nick_callback):
        """We supress certain response codes for readability:
        004: Server mode strings
        005: Server capability report
        317: User away time in /whois TODO: format this sometime
        323: End of /LIST
        333: Topic setter/time
        366: End of /NAMES list
        376: End of /MOTD command
        """
        self.supress_codes = ['004', '005', '317', '323', '333', '376']
        self.replace_msgs = {
            '375': '***SERVER MESSAGE OF THE DAY***',
            '321': '***CHANNEL LISTING***',
            '331': '<<No topic set>>',
            '433': 'Nickname taken. Pick another one with /nick <newnick>'
        }
        self.whois_codes = ['311', '319', '312', '313', '671', '318']
        self.nick = nick
        self.set_nick_callback = set_nick_callback

    def get_nick(self, host):
        nick_format = re.compile(':\w*!')
        match = nick_format.match(host)
        if match:
            nick = match.group()
            nick = nick[1:len(nick)-1] # remove : and !
            return nick
        else:
            return False

    def parse_message(self, message):
        # First try to parse numerically coded messages
        split_message = message.split(' ')
        if len(split_message) < 3:
            return message

        code_format = re.compile('\d\d\d')

        if code_format.match(split_message[1]):
            numeric_code = split_message[1]
            message_body = ' '.join(split_message[3:])
            if message_body[0] == ':':
                message_body = message_body[1:] # Remove extra colons

            if numeric_code in self.replace_msgs:
                message_body = self.replace_msgs[numeric_code]
            elif numeric_code == '001': # update nick on registration
                self.set_nick_callback(split_message[2])
            elif numeric_code == '372': # MOTD body
                message_body = message_body[2:] # Remove '- '
            elif numeric_code == '353': # /names list
                nick_list = ' '.join(split_message[5:])
                message_body = f'Users in {split_message[4]}: {nick_list[1:]}'
            elif numeric_code == '332': # /topic reply
                channel = split_message[3]
                topic = ' '.join(split_message[4:])
                topic = topic[1:]
                message_body = f'Topic for {channel}: {topic}'
            elif self.whois_codes.count(numeric_code) == 1: #/whois reply
                info = ' '.join(split_message[4:])
                message_body = f'[iNFO] {info}'
            
            elif self.supress_codes.count(numeric_code) == 1: # Supress some cruft
                return ''

            # message = f'** {numeric_code}: {message_body}' # for debugging
            message = f'** {message_body}'

        elif split_message[1] == 'NOTICE': # Registered notice
            notice = ' '.join(split_message[4:])
            message = f'** NOTICE: {notice}' 
        elif split_message[0] == 'NOTICE': # AUTH notice
            notice = ' '.join(split_message[3:])
            message = f'** NOTICE: {notice}' 
        elif split_message[1] == 'JOIN': # JOIN messages
            nick = self.get_nick(split_message[0])
            if nick:
                channel = split_message[2]
                message = f'** {nick} has joined {channel[1:]}'
        elif split_message[1] == 'PRIVMSG': # chat messages
            nick = self.get_nick(split_message[0])
            if nick:
                channel = split_message[2]
                message = split_message[3]
                if channel == self.nick:
                    message = f'-{nick}- <{nick}> {message[1:]}'
                else:
                    message = f'-{channel}- <{nick}> {message[1:]}'
        elif split_message[1] == 'PART': # PART messages
            nick = self.get_nick(split_message[0])
            if nick:
                channel = split_message[2]
                try:
                    message = split_message[3]
                    message = ': ' + message[1:]
                except IndexError:
                    message = ''
                message = f'** {nick} has left {channel}{message}'
        elif split_message[1] == 'MODE': # chat messages
            nick = self.get_nick(split_message[0])
            if nick:
                target = split_message[2]
                mode = ' '.join(split_message[3:])
                message = f'** {nick} has set {mode} on {target}'
        elif split_message[1] == 'NICK': # nick changes
            nick = self.get_nick(split_message[0])
            if nick:
                new_nick = split_message[2]
                if nick == self.nick: # Our user is changing nickname
                    self.nick = new_nick[1:]
                    self.set_nick_callback(new_nick[1:])
                    message = f'** You have changed nick to {new_nick[1:]}'
                else: # other user changing nick
                    message = f'** {nick} changed nick to {new_nick[1:]}'
                    

        else:
            logging.debug(f'other msg: {message}')

        return message
