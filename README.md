Mandelbot
====

(Yet another) IRC bot

**I don't actually work yet, but feel free to have a poke around**

===
### Configuration (sample in config_sample.json)
* **name** - the name of the network
* **host** - the address of the IRC network server
* **port** - the port the IRC server listens on
* **ssl** - whether to connect using SSL or not
* **password** - the password for the IRC server (if required)
* **autoconnect** - whether to automatically connect to the IRC server when Mandelbot is launched
* **nickserv** - the identification service on this network
* **username** - used to identify Mandelbot with the IRC server
* **nickpass** - used to identify Mandelbot with the IRC server
* **realname** - used to identify Mandelbot with the IRC server
* **nickname** - used to identify Mandelbot with the IRC server
* **command** - the command identifier Mandelbot listens for on this network
* **owner** - the IRC user who can administrate Mandelbot on this network
* **users** - a list of IRC users who can access Mandelbot's protected functions on this network
* **chans** - a dictionary of the channels Mandelbot is to join, and the key (if required)
