#!/usr/bin/env python3
""" This plugin gives you a nicer overview of the channel balances of your node.

Instead of calling listpeers, with chanbalances you see the outbound and inbound capacity 
for each channel. Also you see the pubkey of channel peer and the alias of peer.

Activate the plugin with: 
`lightningd --plugin=PATH/TO/LIGHTNING/contrib/plugins/funds/chanbalances.py`

Call the plugin with: 
`lightning-cli chanbalances`

The standard unit to depict the funds is set to satoshis. 
The unit can be changed by and arguments after `lightning-cli funds` 
for each call. It is also possible to change the standard unit when 
starting lightningd just pass `--funds_display_unit={unit}` where
unit can be s for satoshi, b for bits, m for milliBitcoin and B for BTC.

Author: lngames.net
Based on the funds plugin of Rene Pickhardt (https://ln.rene-pickhardt.de)

"""

import json

from lightning.lightning import LightningRpc
from lightning.plugin import Plugin
from os.path import join

rpc_interface = None
plugin = Plugin(autopatch=True)

unit_aliases = {
    "bitcoin": "BTC",
    "btc": "BTC",
    "satoshi": "sat",
    "satoshis": "sat",
    "bit": "bit",
    "bits": "bit",
    "milli": "mBTC",
    "mbtc": "mBTC",
    "millibtc": "mBTC",
    "B": "BTC",
    "s": "sat",
    "m": "mBTC",
    "b": "bit",
}

unit_divisor = {
    "sat": 1,
    "bit": 100,
    "mBTC": 100*1000,
    "BTC": 100*1000*1000,
}


@plugin.method("chanbalances")
def funds(unit=None, plugin=None):
    """Lists the balances for all lightning node channels  {unit}.

    {unit} can take the following values:
    s, satoshi, satoshis to depict satoshis
    b, bit, bits to depict bits
    m, milli, btc to depict milliBitcoin
    B, bitcoin, btc to depict Bitcoins

    When not using Satoshis (default) the comma values are rounded off."""

    plugin.log("call with unit: {}".format(unit), level="debug")
    if unit is None:
        unit = plugin.get_option("funds_display_unit")

    if unit != "B":
        unit = unit_aliases.get(unit.lower(), "sat")
    else:
        unit = "BTC"

    div = unit_divisor.get(unit, 1)

    funds = rpc_interface.listfunds()

    channels_num=0

    channel={}
    mydata={}
    mydata['channels']=[]
    channels=mydata['channels']
    capacity_value=0
    outbound_value=0



    for x in funds["channels"]:
        capacity_value = capacity_value+int(x["channel_total_sat"])
        outbound_value = outbound_value+int(x["channel_sat"])
        channels_num=channels_num+1
        channel={ 'id': x["short_channel_id"], 
                    'peer_id': x['peer_id'],
                    'alias': plugin.rpc.listnodes(x['peer_id'])['nodes'][0]['alias'],
                    'capacity_'+unit: x["channel_total_sat"]//div,
                    'outbound_'+unit: x["channel_sat"]//div,
                    'inbound_'+unit: (x["channel_total_sat"]-x["channel_sat"])//div,
                    'outbound_percent': int((x["channel_sat"]/x["channel_total_sat"])*100),
                    'inbound_percent': int(((x["channel_total_sat"]-x["channel_sat"])/x["channel_total_sat"])*100),
                    }

        channels.append(channel)

    inbound_value = capacity_value - outbound_value

    resum={'channels': channels_num,
            'capacity_'+unit: capacity_value//div,
            'outbound_'+unit: outbound_value//div,
            'inbound_'+unit: inbound_value//div,
            'outbound_percent': int((outbound_value/capacity_value)*100),
            'inbound_percent': int((inbound_value/capacity_value)*100),    
        }

    mydata['total']=resum

    return mydata


@plugin.init()
def init(options, configuration, plugin):
    global rpc_interface
    plugin.log("start initialization of the chanbalances plugin", level="debug")
    basedir = configuration['lightning-dir']
    rpc_filename = configuration['rpc-file']
    path = join(basedir, rpc_filename)
    plugin.log("rpc interface located at {}".format(path))
    rpc_interface = LightningRpc(path)
    plugin.log("Chanblances successfully initialezed")
    plugin.log("standard unit is set to {}".format(
    plugin.get_option("funds_display_unit")), level="debug")


# set the standard display unit to satoshis
plugin.add_option('funds_display_unit', 's',
                  'pass the unit which should be used by default for the simple chanbalances overview plugin')
plugin.run()
