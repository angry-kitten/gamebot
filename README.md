# gamebot

The main gamebot project is a hobby project. The plan is to create python code that plays games. The first game will be ACNH. The python code will use https://github.com/angry-kitten/gamebot-usb-serial to provide control input to the console. A webcam will be used to get feedback from the console. On the PC the webcam video will be captured by OpenCV. Some of the python code will use the frames directly. The frames will also be fed to TensorFlow for object recognition. With the full feedback loop the game playing code should be capable of very complex operations that just aren't possible with the programs that have no feedback, like the snowball thrower.

I've played ACNH and pretty much finished it. And a little bored with it. Time to sick the machines on it. Learning about OpenCV and TensorFlow may help with my Real Job (tm). That's my story and I'm sticking to it. In any case it'll be a nice puzzle to work on.

The plan is to keep everything in the same repository at first. When it comes time to try a different game from ACNH, the ACNH part will be split out into its own repository.
