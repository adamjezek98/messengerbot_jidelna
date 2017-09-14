# messengerbot_jidelna
Messengerbot for menu at our school canteen

webhook.py listens for POST from Facebook
sender.py is made for sending messages
botconfig.py has the config like access_token or SSL certs
download_menu.py downloads PDFs with menus from school website and parses them
send_menu.py sends the menu to subscribed users (runned by cron every hour)
