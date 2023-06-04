import requests
import time
import telebot
import threading
import logger as l
import api_token as t

# Telegram API token
BOT = t.token


class Service:
    """Service params"""
    def __init__(self, name: str, url: str, ping_break_time: int):

        # Service params
        self.name = name
        self.url = url
        self.ping_break_time = ping_break_time

        # UI Buttons
        self.button = telebot.types.InlineKeyboardMarkup()
        self.button.add(telebot.types.InlineKeyboardButton(f'Visit {self.name}', url=self.url))

        # UI Messages
        self.msg_down = f'\U0000203C\U0000203C\U0000203C {self.name} Down: '
        self.msg_recover = f'\U00002705\U00002705\U00002705 {self.name} Recovered: '
        self.msg_timeout = f'\U0000203C\U0000203C\U0000203C {self.name} Server Timeout'
        self.msg_start = f'\U0001F6E1 {self.name} monitoring started ...'

    def parse(self) -> list:
        """ Get service response headers"""
        get_url = requests.get(self.url)
        url_status = [get_url.status_code, get_url.reason]
        return url_status

    def send_start_message(self, message):
        """Send Notification monitoring started"""
        BOT.send_message(message.chat.id, self.msg_start)

    def send_timeout_message(self, response, message):
        """Send Notification server timeout"""
        BOT.send_message(message.chat.id, self.msg_timeout, reply_markup=self.button)
        l.logger.info(f'{self.name} timeout: {response} received')
        time.sleep(self.ping_break_time)

    def send_down_message(self, response, message):
        """Send Notification server down"""
        BOT.send_message(message.chat.id, f'{self.msg_down}{response}', reply_markup=self.button)
        l.logger.info(f'{self.name} server down reason: {response}')
        time.sleep(self.ping_break_time)

    def send_recover_message(self, response, message):
        """Send Notification server recovered"""
        BOT.send_message(message.chat.id, f'{self.msg_recover}{response}', reply_markup=self.button)
        l.logger.info(f'{self.name} up after timeout: {response} received')
        time.sleep(self.ping_break_time)


if __name__ == '__main__':

    # Services initializing Name, URL, ping_time seconds
    service_1 = Service('service_1_name_here', 'url_service_1_name_here', 60)
    service_2 = Service('service_2_name_here', 'url_service_1_name_here', 60)

    # Services list for thread processing
    services_list = [service_1, service_2]


    def scan_site(message, service):
        """
        Receives response header (status code, reason) from service
        then sends correspond to issue Notification to user in case if issue happened
        """

        while True:
            response = service.parse()
            if response is None:
                service.send_timeout_message(response, message)
                while response is None:
                    response = service.parse()
                    if response[0] == 200:
                        service.send_recover_message(response, message)
            elif response[0] != 200:
                service.send_down_message(response, message)
                while response[0] != 200:
                    response = service.parse()
                    if response[0] == 200:
                        service.send_recover_message(response, message)
            else:
                time.sleep(service.ping_break_time)

    @BOT.message_handler()
    def start(message):
        """
        Receives any message from user which includes telegram bot parameters needed for
        interaction with code. Then processing  services list, run monitoring for each in
        and send Notification to user 'service_name' monitoring started
        """
        for service in services_list:
            thread = threading.Thread(target=scan_site, args=(message, service))
            thread.start()
            service.send_start_message(message)


    BOT.polling(none_stop=True)
