#!/usr/bin/env python3
""" This plugin send warnings and resumes to telegrambot. So you can be notified when 
there are changes in your c-lightning node funds.

check_interval: specifies the interval in seconds that funds on node are checked.
check_resume_num: #send status every check_resume_num (e.g: if check_interval is 60 sec, and chec_resum_num=60, the plugin will send a resum every hour)

Activate the plugin with: 
`lightningd --plugin=PATH/TO/LIGHTNING/contrib/plugins/funds/telegrambot.py`

Or add the plugin to your plugins dir.

The plugins run as daemon once the lightningd is started.

This is just a simple example, it can be improved in many ways (telegrambot interaction, more warnings and resumes, etc)

Author: lngames.net

"""

import requests
import json
from time import sleep, time
import threading
import heapq
from lightning.lightning import LightningRpc
from lightning.plugin import Plugin
from os.path import join
from datetime import datetime

rpc_interface = None
plugin = Plugin(autopatch=True)

#TELLEGRAM INFO AND GLOBAL VARS.
telegram_token = 'YOUR_TELEGRAM_TOKEN' #your telegrambot api key
telegram_userid = 'YOUR_TELEGRAM_USERID' #your telegram uid.
check_interval=60 #check interval in seconds.
check_resume_num=60 #send status every check_resume_num (e.g: if check_interval is 60 sec, and chec_resum_num=60, the plugin will send a resum every hour)
total_funds_old=0
checks_counter=0

#TELEGRAM SEND MESSAGE
def telegrambot_send(bot_message):
    send_text = 'https://api.telegram.org/bot' + telegram_token + '/sendMessage?chat_id=' + telegram_userid + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


#START PLUGIN DAEMON
def start_telegrambot(plugin):
    t = threading.Thread(target=telegrambot, args=[plugin])
    t.daemon = True
    t.start()

#SCHEDULER
def schedule(plugin):
    # List of scheduled calls with next runtime, function and interval
    next_runs = [
        (time() + check_interval, start_telegrambot, check_interval)
    ]
    heapq.heapify(next_runs)

    while True:
        n = heapq.heappop(next_runs)
        t = n[0] - time()
        if t > 0:
            sleep(t)
        # Call the function
        n[1](plugin)

        # Schedule the next run
        heapq.heappush(next_runs, (time() + n[2], n[1], n[2]))



@plugin.method("telegrambot")
def telegrambot(interval=60,  plugin=None):
    """Send telegrambot warnings when funds on your node change.
	"""
    global total_funds_old
    global checks_counter
    global check_resume_num
    

    #FUNDS:
    funds = rpc_interface.listfunds()
    onchain_value = sum([int(x["value"]) for x in funds["outputs"]])
    offchain_value = sum([int(x["channel_sat"]) for x in funds["channels"]])

    total_funds = onchain_value + offchain_value

    dif=total_funds-total_funds_old
    funds_txt='Total: '+str(total_funds)+'\n Onchain: '+str(onchain_value)+'\n Channels: '+str(offchain_value)+'\n dif: '+str(dif)

    #WARNING FUNDS CHANGED
    if checks_counter==0:
        checks_counter=checks_counter+1
        print(str(datetime.now())+' first check')
        total_funds_old=total_funds
    else:
        checks_counter=checks_counter+1
        msg='*WARNING NODE FUNDS:*\n'+funds_txt
        if total_funds != total_funds_old:
            print(str(datetime.now())+msg)
            total_funds_old=total_funds
            telegrambot_send(msg)

    #SEND FUNDS RESUME:
    if check_resume_num > 0:
    	if checks_counter >= check_resume_num:
    		msg='*RESUME NODE FUNDS:*\n'+funds_txt
    		telegrambot_send(msg)
    		print('New cicle')
    		checks_counter=0


@plugin.init()
def init(options, configuration, plugin):
    global rpc_interface
    plugin.log("start initialization of the telegrambot plugin", level="debug")
    basedir = configuration['lightning-dir']
    rpc_filename = configuration['rpc-file']
    path = join(basedir, rpc_filename)
    plugin.log("rpc interface located at {}".format(path))
    rpc_interface = LightningRpc(path)
    plugin.log("telegrambot Plugin successfully initialezed")
    t = threading.Thread(target=schedule, args=[plugin])
    t.daemon = True
    t.start()

# set the standard display unit to satoshis
plugin.add_option('funds_display_unit', 's',
                  'pass the unit which should be used by default for the simple funds overview plugin')


plugin.run()
