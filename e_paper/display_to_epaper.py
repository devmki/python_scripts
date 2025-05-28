"""
This script displays weather data, waste retrieval and birthdays 
on an e-paper display using the Open Meteo API.
"""
import time
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import pytz
import numpy as np
import epaper
from meteo_data import open_meteo_data as omd
from birthday_push_message import scheduler as sh
from abfallkalender import read_abfall_ics

# Define values for latitude and longitude
LATITUDE = 0.0  # Replace with your latitude
LONGITUDE = 0.0 # Replace with your longitude

# Define the path to the weather icons
PATH_TO_ICONS = 'your_path_to_weather_icons'  # Replace with the actual path to your weather icons

# dicts and lists
days_dict = {
    'Monday':'Montag',
    'Tuesday': 'Dienstag',
    'Wednesday': 'Mittwoch',
    'Thursday': 'Donnerstag',
    'Friday': 'Freitag',
    'Saturday' : 'Samstag',
    'Sunday': 'Sonntag'
}

units_list = ['[°C]', '[°C]', '[%]', '[mm]', '[%]', '[-]']

measurements_list = ['Temperatur 2m', 'Temp. gefühlt', 'Luftfeuchte',
                     'Niederschlag', 'Probability', 'UV-Index']    

def draw_text_in_table_format(draw, text_list, x_start, y_start, x_offset, y_offset, font, fill=0):
    """
    Draws text in a table format on the image.
    """
    for element in text_list:
        draw.text((x_start, y_start), element, font=font, fill=fill)
        x_start += x_offset
        y_start += y_offset

def display_weather_on_epaper():
    """
    Main function to display weather data on the e-paper display.
    """
    # Initialize the e-paper display
    epd = epaper.epaper('epd7in5_V2').EPD()
    epd.init()
    epd.Clear()

    # Create a blank image for drawing
    image = Image.new('1', (epd.width, epd.height), 255)  # 1: black and white
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)

    # Fetch weather data
    weather = omd.OpenMeteoWeather(latitude=LATITUDE, longitude=LONGITUDE)

    #hourly data
    hourly_data = weather.get_weather_hourly()

    #daily data
    daily_data = weather.get_weather_daily()

    #current time
    local_tz = pytz.timezone('UTC')
    hour_now = datetime.now().replace(minute=0, second=0, microsecond=0)
    hour_now = local_tz.localize(hour_now)

    day_now = datetime.now()
    tomorrow = day_now + timedelta(days=1)
    day_after_tomorrow = day_now + timedelta(days=2)

    #current day
    draw.text((10,10), f'{days_dict[day_now.strftime("%A")]}, {day_now.strftime("%d.%m.%Y")}',
               font=font, fill=0)

    #get weather icons
    # Get weather icons for the next 4 hours (hour_now to hour_now + 3)
    icons = weather.images_of_weather_icons(PATH_TO_ICONS,
                                            hourly_data.loc[hour_now:hour_now + timedelta(hours=3)])

    #take out trash?
    # Construct the relative path dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ics_file_path = os.path.join(script_dir, f'../abfallkalender/abfallkalender{day_now.year}.ics')
    trash_days = read_abfall_ics.get_events_for_today_and_tomorrow(ics_file_path)
    if trash_days:
        x_start = 500
        y_start = 380
        for trash_day in trash_days:
            if trash_day['start'] == day_now.date():
                draw.text((x_start, y_start), f'Heute: {trash_day["summary"]}', font=font_small, fill=0)
                y_start += 20
            elif trash_day['start'] == tomorrow.date():
                draw.text((x_start, y_start + 20), f'Morgen: {trash_day["summary"]}', font=font_small, fill=0)
                y_start += 20

    #display temmperature min/max of current day
    draw.text((10,70), 'Temp min/max', font=font, fill=0)
    draw.text((230,70),
              f'{str(round(daily_data.iloc[0,0],1))} / {str(round(daily_data.iloc[0,1],1))}'
              , font=font, fill=0)

    # Display the first few hours of weather data
    draw_text_in_table_format(draw, measurements_list, 10, 110, 0, 40, font)
    draw_text_in_table_format(draw, units_list, 250, 110, 0, 40, font)

    x_offset = 375
    #hourly data
    for hour_offset in range(4):
        y_offset = 45
        hour = hour_now + timedelta(hours=hour_offset)
        if hour in hourly_data.index:
            row = hourly_data.loc  [hour]
            draw.text((x_offset,10), f"{hour.strftime('%H:%M')}", font=font, fill=0)
            image.paste(icons [hour_offset], (x_offset + 10, y_offset))
            y_offset = 110
            for value in range(len(row)):
                if value < len(row) - 2:
                    rounded_val = np.round(row.iloc[value],1)
                    rounded_val = str(rounded_val)
                    if len(rounded_val) > 3:
                        draw.text((x_offset + 10,y_offset), rounded_val, font = font, fill=0)
                    else:
                        draw.text((x_offset + 26,y_offset), rounded_val, font = font, fill=0)
                    y_offset += 40
            x_offset += 110

    #display daily data
    draw.text((10,380), 'Temp min/max', font=font_small, fill=0)
    draw.text((10,400), 'N-Summe', font=font_small, fill=0)
    draw.text((10,420), 'Beschreibung', font=font_small , fill=0)

    x_offset = 180
    for index in daily_data.index:
        y_offset = 360
        if index.date() == tomorrow.date() or index.date() == day_after_tomorrow.date():
            row = daily_data.loc[index]
            draw.text((x_offset,y_offset), days_dict[index.strftime('%A')], font=font_small, fill=0)
            #temperature
            y_offset += 20
            str_vals = f'{str(round(row.iloc[0],0))} / {str(round(row.iloc[1],0))}'
            draw.text((x_offset,y_offset), str_vals, font=font_small, fill=0)
            #precipitation sum
            y_offset += 20
            str_vals = str(round(row.iloc[3],0))
            draw.text((x_offset,y_offset), str_vals, font=font_small, fill=0)
            #description
            y_offset += 20
            str_vals = weather.weather_code_translations[row.iloc[2]].split(':')[0]
            draw.text((x_offset,y_offset), str_vals, font=font_small, fill=0)
            x_offset += 150


    #birthday list:
    birthdays = sh.check_and_send_birthdays('nothing', mode='do_not_send')
    if birthdays:
        x_offset = 500
        y_offset = 340
        for birthday in birthdays:
            draw.text((x_offset,y_offset), birthday, font = font_small, fill=0)
            y_offset += 20

    # Display the image on the e-paper
    epd.display(epd.getbuffer(image))
    time.sleep(2)

    # Put the display to sleep
    epd.sleep()

if __name__ == "__main__":
    display_weather_on_epaper()
