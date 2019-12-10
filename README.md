# C-LIGHTNING PLUGINS

Some basic and useful plugins for c-lightning.

## Plugins
### chanbalances:  

Show nicer overview of the channel balances of your node. Whith chanbalances you see the outbound and inbound capacity 
for each channel. Also you see the pubkey and alias of channel peer. [chanbalances.py](https://github.com/lngamesnet/c-lightning-plugins/blob/master/chanbalances.py)

### telegrambot:  

Receive warnings and monitor your c-lightning node via Telegram Bot. Whith this simple example you can receive warnings when there are variations in the funds of your node, and a periodic report about your funds. It should be easy to add more warnings and monitoring data: channels, invoices, payments, etc.  [telegrambot.py](https://github.com/lngamesnet/c-lightning-plugins/blob/master/telegrambot.py)


### summary2: 

Extended version of [summary plugin](https://github.com/lightningd/plugins/tree/master/summary) . It shows more detailed info about listed channels (chan Id, capacity, in sats, out sats, %,...) [summary2.py](https://github.com/lngamesnet/c-lightning-plugins/blob/master/summary2.py)

## Resources

-[c-lightning](https://github.com/ElementsProject/lightning)

-[Rene Pckhardt plugin collection](https://github.com/renepickhardt/c-lightning-plugin-collection)

-[conscott plugins](https://github.com/conscott/c-lightning-plugins)

-[Community curated plugins for c-lightning](https://github.com/lightningd/plugins)
