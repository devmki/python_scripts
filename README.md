# A collection of scripts for use with Raspberry Pi and Waveshare 7.5in V2 epaper 

## Modules

### abfallkallender
read_abfall_kalender.py reads the dates of garbage pickup from a ics file using icalendar.

### birthday_push_message
A small gui application to store birthdays in a sqlite database. The main.py can be called via the command line for automation of push message notification to your device via pushbullet. Before this can be done you must
have a pushbullet API key. Parts of these scripts are also used to display birthdays on the epaper.

### meteo_data
This script gets hourly and daily forecasts for a location specified by the user.

### e_paper
The main display script which utilizes the others to display current weather data, the garbage pickup schedule and birthdays.

1. Before running the latitude, longitude and the path to weather icons must be set. Weather icons must have the bmp file format.
2. run by using `python3 -m e_paper.display_to_epaper`
