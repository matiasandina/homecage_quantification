# Homecage Quantification

This project contains code to establish a monitoring system based on raspberry Pi 4 and cameras. 

If using FED3 devices to quantify food intake, go to [this repository](https://github.com/matiasandina/FED_quantification) to find the code.

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

On a fresh Raspberry Pi open a terminal and run:

```
git clone https://github.com/matiasandina/homecage_quantification.git
cd homecage_quantification
bash setup.sh
```

## Usage

## Contribute

This is a preliminary release. Please file issues to improve the functioning.