# Homecage Quantification

This project contains code to establish a monitoring system based on raspberry Pi 4 and cameras. 

If using FED3 devices to quantify food intake, you can also find a data analysis tool in [this repository](https://github.com/matiasandina/FED_quantification).

## Main aspects of Homecage quantification

1. Acquire video 
	* Stream to a local network to be visualized by other computers in the network (via IP).
	* Record video to local file. 
1. Perform optical flow quantification on video.
1. Record mouse temperature using FLIR lepton 3.5 and openMV.

### More modules 

1. Ambient Temperature and Humidity ([See here](https://github.com/matiasandina/temp_sensor)).
1. Code for analysis of FED3 device ([See here](https://github.com/matiasandina/FED_quantification))

## Usage

For detailed usage refer to the [Wiki page](https://github.com/matiasandina/homecage_quantification/wiki).

## Contribute

This is a preliminary release. Please file issues to improve the functioning.