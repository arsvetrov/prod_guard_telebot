import telebot
from bot import Service

# Telegram API token
BOT = telebot.TeleBot('6003125715:AAHuxf3xodCPNWIzHG1G3T09gVXQwgjCYHw')

# Services list initializing Name, URL, ping_timeout seconds
services_list = [

    Service('Facebook', "https://uk-ua.facebook.com/", 3),
    Service('Google', 'https://google.com', 3),

]
