# ME556_Final
This is the Arduino and Python code for the PSU FA2024 ME556 Final Project

The code was developed using Microsoft VSCode.
The Python code was directly interpreted by VSCode.
The PlatformIO plug-in was used inside VSCode to interface with the NodeMCU32-S microcontroller controlling the rover.

The microcontroller was programmed using the Arduino language.
Main.cpp runs the rover.
The two header files are required to interface with Bluetooth serial communications and the motors.

kinematicModel.py showed good model tracking by generating a trajectory, using inverse kinematics to generate motor speeds, then properly tracking the trajectory using forward kinematics.
commandAndSensingPlatform.py was the human-robot interface used to develop the link between the sensors, the microcontroller, and a mapping platform.
The mapping platform was the tkinter library for python.
Both python scripts require the tkinter library 

This project did not reach the point of having the robot do autonomous mapping.
