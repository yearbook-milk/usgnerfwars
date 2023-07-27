# README.txt

This is a Python helper program to facilitate the transfer of commands, live video data, and other information between the USG Nerf Drone and a control computer.

--------------------
On the client side (which will be the remote laptop in the drone project), a program receives UDP data from the server side (which will be the actual USG Nerf Drone) as well as being able to send/receive TCP packets. It cannot send UDP packets of its own; it only takes in data. The flow of UDP packets is one way, from server to client. The TCP packets go two ways however so that way the user can commanbd the drone and the drone can reliably report data back to the user.

On the server side, the program can send UDP data to the client without blocking, while also being able to check for and send TCP packets without blocking (this way, the drone can continually be processing images, and if there is no external commands coming from the user, Python will not block waiting for datra to come in via the socket. Instead, if there are no instructions or data to read, it just keeps going). 

This repo is just for our team - we're probably not going to publish detailed documentation on GitHub.
