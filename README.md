# techmastercal
Caltech Master Calendar Project

This project uses Python and the Beautiful Soup package to pull events from the caltech master calendar site 
(https://www.caltech.edu/master-calendar/day) and create .ics files for each event. 
I have created a launchctl plist which will run the python script each day at midnight. From there, the user can import 
the .ics files into their calendar application manually. 

The next stage of development is to write a script which can automatically import all .ics files.
