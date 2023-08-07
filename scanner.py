from api_token import *
from logger import *
from services import *
import requests
import time
import threading


class Service:
    """Service params."""
    def __init__(self, name: str, url: str, ping_break_time: int):

        # Service params
        self.name = name
        self.url = url
        self.ping_break_time = ping_break_time

    def get_service(self) -> list:
        """ Get service response headers."""
        get_url = requests.get(self.url, timeout=10)
        url_status = [get_url.status_code, get_url.reason]
        time.sleep(self.ping_break_time)
        return url_status


class Bot(Service):
    """Bot UI items"""
    def __init__(self, name, url):
        super().__init__(name, url, ping_break_time=0)

        # Bot UI buttons
        self.button = telebot.types.InlineKeyboardMarkup()
        self.button.add(telebot.types.InlineKeyboardButton(f'Visit {self.name}', url=self.url))

        # Bot UI messages text
        self.msg_down = f'\U0000203C\U0000203C\U0000203C {self.name} Down: '
        self.msg_recover = f'\U00002705\U00002705\U00002705 {self.name} Recovered: '
        self.msg_timeout = f'\U0000203C\U0000203C\U0000203C {self.name} Server Timeout '
        self.msg_start = f'\U0001F6E1 {self.name} monitoring started ...'

    # Bot send messages
    def start_message(self, message):
        """Send Notification monitoring started."""
        bot.send_message(message.chat.id, self.msg_start)

    def timeout_message(self, response, message):
        """Send Notification server timeout."""
        bot.send_message(message.chat.id, self.msg_timeout, reply_markup=self.button)
        logger.error(f'{self.name} timeout: {response} received')

    def down_message(self, response, message):
        """Send Notification server down."""
        bot.send_message(message.chat.id, f'{self.msg_down}{response}', reply_markup=self.button)
        logger.error(f'{self.name} server down reason: {response}')

    def recover_message(self, response, message):
        """Send Notification server recovered."""
        bot.send_message(message.chat.id, f'{self.msg_recover}{response}', reply_markup=self.button)
        logger.info(f'{self.name} restored: {response} received')


if __name__ == '__main__':

    def service_time_out(timeout, service, bot_ui, message):
        """Time out handle function. Sends user message that server
        got timeout then wait when server will be recovered  then notify
        user that server up."""

        bot_ui.timeout_message(timeout, message)
        while timeout:
            try:
                response = service.get_service()
            except Exception:
                continue
            else:
                if response[0] == 200:
                    bot_ui.recover_message(response, message)
                    break

    def service_down(bot_ui, response, message, service):
        """Incorrect status code handle function. Sends user message when
        not 200 code got. Then wait when server will receive 200 code then
        notify user that server up."""

        bot_ui.down_message(response, message)
        while response[0] != 200:
            response = service.get_service()
            if response[0] == 200:
                bot_ui.recover_message(response, message)

    def scan_site(message, service):
        """
        Main monitoring function.
        """
        bot_ui = Bot(service.name, service.url)
        bot_ui.start_message(message)

        while message:
            try:
                response = service.get_service()
            except Exception as timeout:
                service_time_out(timeout, service, bot_ui, message)
            else:
                if response[0] != 200:
                    service_down(bot_ui, response, message, service)


    @bot.message_handler()
    def start(message):
        """
        Receives any message from user in telegram chat.
        Then processing of services list starts.
        The monitoring for each service starts.
        """
        for service in services_list:
            thread = threading.Thread(target=scan_site, args=(message, service))
            thread.start()

    bot.polling(none_stop=True)
