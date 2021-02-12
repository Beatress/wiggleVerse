import re
import logging

class ServerParser:
    def __init__(self):
        pass

    def parse_message(self, message):
        # First try to parse numerically coded messages
        split_message = message.split(' ')
        if len(split_message) < 4:
            return message

        code_format = re.compile('\d\d\d')
        if code_format.match(split_message[1]):
            numeric_code = split_message[1]
            message_body = ' '.join(split_message[3:])
            message = f'** {numeric_code}: {message_body}'
        elif split_message[1] == 'NOTICE': # Registered notice
            notice = ' '.join(split_message[4:])
            message = f'** NOTICE: {notice}' 
        elif split_message[0] == 'NOTICE': # AUTH notice
            notice = ' '.join(split_message[3:])
            message = f'** NOTICE: {notice}' 
        else:
            logging.debug(f'other msg: {message}')

        return message
