My first Raspberry Pi project. 

The scripts display a variety of data on a Waveshare 7.5in_V2 epaper display. 
abfallkallender - read_abfall_kalender.py reads the dates of garbage pickup from a ics file using icalendar
birthday_push_message - a small gui application to store birthdays in a sqlite database. the main.py can be called via the command line
                        for automation of push message notification to your device via pushbullet. before this can be done you must
                        have a pushbullet API key.
                        parts of these scripts are also used to display birthdays on the epaper.
meteo_data - this script gets hourly and daily forecasts for a location specified by the user
e_paper - the main display script which utilizes the others to display current weather data, garbage pickup schedule, birthdays
          To run latitude, longitude and the path to weather icons must be set. weather icons must have the bmp file format.
