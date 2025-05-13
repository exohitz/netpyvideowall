# netpyvideowall
Network based Python Videowall and Player

Uses any NDI input (named "Screen 1") and splits it based on the Drawio input and streams it as NDI Output

Used Librarys:
https://pypi.org/project/cyndilib/

https://opencv.org/

## Tutorial
1. install dependencies:
	```
	pip install cyndilib opencv-python
	```
2. create a funny shape with squares in Drawio (use input2.xml as template)
3. export the XML of the Drawio darwing, name it input2.xml, past it in the same folder as the other files
4. run videowallv1-drawiomaper.py (this will create a .json file with the coordinates
5. run videowallv1.py this will start streaming ndi imediatly
6. run client.py on any network joined client to start recieving ndi streams. (matching hostnames to squarenames from drawio)


# disclaimer
this code is a proof of concept an will be improved in the future.

## known or unknown issues
- Client timing not jet tested
- Jittering on the client.py
- CPU heavy, looking forward to use OPENGL or CUDA