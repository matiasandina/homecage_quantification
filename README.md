# Homecage Quantification

This project contains code to establish a monitoring system based on raspberry Pi 4 and cameras. 

If using FED3 devices to quantify food intake, go to [this repository](https://github.com/matiasandina/FED_quantification) to find the analysis code and go to `DOCS.md` to find more information.

## Main aspects of Homecage quantification

1. Acquire video 
	* Stream to a local network to be visualized by other computers in the network (via IP).
	* Record video to local file. 
1. Perform optical flow quantification on video.
1. Record mouse temperature using FLIR lepton 3.5 and openMV.

### More modules 

1. Ambient Temperature and Humidity.
1. Code for analysis of FED3 device ([See here](https://github.com/matiasandina/FED_quantification))


## Install

### Raspbian install

Follow raspbian wizard to setup timezone and language.
Connect to MIT network.
Check for updates (that will take a while).

### Enable all interfaces

Go to the menu (top left corner)

`Preferences >  Raspberry Pi Configuration`

Go to the Interfaces tab. Enable all of them.


### Clone repository

Open a terminal and run (CTRL+Shift+V):

```
git clone https://github.com/matiasandina/homecage_quantification.git
```

### Install dependencies

Then, navigate to the folder

```
cd homecage_quantification/
```

And start the setup for that computer by running.

```
bash setup.sh
```

This script will install necessary libraries and configuration for the homecage quantification to run

### ssh setup

The last step of the setup.sh will prompt you to connect to choilab pc.

it will ask 

```
Are you sure you want to continue connecting (yes/no)?
```

Answer "yes". And then you will be asked for the choilab pc password.

After that, you should see the following message:

```
Number of key(s) added: 1

Now try logging into the machine with: "ssh choilab@10.93.6.88"
and check to make sure that only the key(s) you wanted were added.
```

You don't need to log in. You can close the terminal.

### Project setup

## Usage

## Contribute

This is a preliminary release. Please file issues to improve the functioning.