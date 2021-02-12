import re
import logging

class ServerParser:
    def __init__(self):
        """We supress certain response codes for readability:
        004: Server mode strings
        005: Server capability report
        323: End of /LIST
        366: End of /NAMES list TODO: PARSE or re-remove?
        376: End of /MOTD command
        """
        self.supress_codes = ['004', '005', '323', '376']
        self.replace_msgs = {
            '375': '***SERVER MESSAGE OF THE DAY***',
            '321': '***CHANNEL LISTING***',
            '331': '<<No topic set>>',
        }

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
            elif numeric_code == '372': # MOTD body
                message_body = message_body[2:] # Remove '- '
            elif numeric_code == '353': # /names list
                nick_list = ' '.join(split_message[5:])
                message_body = f'Users in {split_message[4]}: {nick_list[1:]}'
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
            nick_format = re.compile(':\w*!')
            nick = nick_format.match(split_message[0]).group()
            nick = nick[1:len(nick)-1] # remove : and !
            channel = split_message[2]
            message = f'** {nick} has joined {channel[1:]}'

        else:
            logging.debug(f'other msg: {message}')

        return message
