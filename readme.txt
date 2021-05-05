Welcome to SpotiLast!


Description:
SpotiLast is a tool that allows you to view your last.fm listening data in various ways. You
can sort and search through your listening data using various filters. SpotiLast also has a
graph feature where you can view your listening data in three different graph types and multiple
filters. Selected songs from the search page can then be exported to a spotify playlist.

How to run:
- install the necessary libraries (see section below)
- run spotilast.py

Libraries:
The libraries that need to be installed that don't come natively with python are:
	- requests
	- spotipy
		-notes for spotipy: the first time you try to create a spotify playlist with spotilast,
		you will get redirected to a link, and you must paste this link into your python terminal. 

Directions for installation: (from 112 website)
	For Windows:
		Run this Python code block in your main Python file (it will print the commands you need to paste into your command prompt):
			import sys
			print(f'"{sys.executable}" -m pip install spotipy')
			print(f'"{sys.executable}" -m pip install requests')
		Open Command Prompt as an administrator user (right click - run as administrator)
		Copy-paste each of the two commands printed in step 1 into the command prompt you opened in step 2.
		Close the command prompt and close Python.
		Re-open Python, and you're set (hopefully)!

	For Mac or Linux:
		Run this Python code block in your main Python file (it will print the commands you need to paste into your command prompt):
			import sys
			print(f'sudo "{sys.executable}" -m pip install spotipy')
			print(f'sudo "{sys.executable}" -m pip install requests')
		Open Terminal
		Copy-paste each of the two commands printed in step 1 into the command prompt you opened in step 2.
		If you see a lock and a password is requested, type in the same password that you use to log into your computer.
		Close the terminal and close Python.
		Re-open Python, and you're set (hopefully)!

	You also need a spotify API key and secret. You can create this at https://developer.spotify.com/dashboard/applications
		
Shortcut Commands:
Press the up arrow on the splash screen to load in test data.