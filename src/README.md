# Kerbal-ELK-Grafana

## About

### What is the software application?

### Who’s it intended for?

### What problem does the software solve?

### How is it going to work?

### What are the main concepts that are involved and how are they related?

## Features
* Real-time sync with the KSP.
* Accessible over the LAN, from any device which is powerful enough.

## Dependencies

* kRPC
* pylogbeat
  
## Setup

* Install kRPC dependencies for Python:
```sh
$ pip install krpc protobuf==3.20.1  
```
* Install pylogbeat
```sh
$ pip install pylogbeat
```
* Run the KSP and start any save game (or start a new one).
* Open the kRPC menu and add a new server.
* Click on *Show advanced settings* and check *Auto-start server* and *Auto-accept new clients*.
Done!

## Usage
* Run server script (from the desktop shortcut or from the main file which includes *KerbalTerminal.py*).
* Connect to your computer's local IP address and 5000 as the port (or localhost if you are using the same computer) on your browser on your device preferably from another computer or from which KSP is installed (ex. localhost:5000 or 127.0.0.1:5000 or 192.168.1.102:5000).

## Special Thanks
...
