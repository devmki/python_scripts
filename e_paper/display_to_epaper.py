import time
import epaper
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from meteo_data import open_meteo_data as omd
import pytz
import numpy as np
from birthday_push_message import scheduler as sh
from abfallkalender import read_abfall_ics
import os


# Define values for latitude and longitude
latitude = 0.0  # Replace with your latitude
longitude = 0.0 # Replace with your longitude

# Define the path to the weather icons
path_to_icons = 'your_path_to_weather_icons'  # Replace with the actual path to your weather icons


days_dict = {
    'Monday':'Montag',
    'Tuesday': 'Dienstag',
    'Wednesday': 'Mittwoch',
    'Thursday': 'Donnerstag',
    'Friday': 'Freitag',
    'Saturday' : 'Samstag',
    'Sunday': 'Sonntag'
}


def display_weather_on_epaper():
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
    weather = omd.OpenMeteoWeather(latitude=latitude, longitude=longitude)
    hourly_data = weather.get_weather_hourly()

    #current time
    local_tz = pytz.timezone('UTC')
    hour_now = datetime.now().replace(minute=0, second=0, microsecond=0)
    hour_now = local_tz.localize(hour_now)

    day_now = datetime.now()
    tomorrow = day_now + timedelta(days=1)
    day_after_tomorrow = day_now + timedelta(days=2)

    #current day
    draw.text((10,10), f'{days_dict[day_now.strftime("%A")]} der {day_now.strftime("%d.%m.%Y")}', font=font, fill=0)

    #get weather icons
    # Get weather icons for the next 4 hours (hour_now to hour_now + 3)
    icons = weather.images_of_weather_icons(path_to_icons,hourly_data.loc[hour_now:hour_now + timedelta(hours=3)])

    #take out trash?
    # Construct the relative path dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ics_file_path = os.path.join(script_dir, f'../abfallkalender/abfallkalender{day_now.year}.ics')
    print('ics_file_path: ', ics_file_path)
    trash_days = read_abfall_ics.get_events_for_today_and_tomorrow(ics_file_path)
    if trash_days:
        for trash_day in trash_days:
            if trash_day['start'].date() == day_now.date():
                draw.text((180, 10), f'Heute: {trash_day["summary"]}', font=font, fill=0)
            elif trash_day['start'].date() == tomorrow.date():
                draw.text((300, 10), f'Morgen: {trash_day["summary"]}', font=font, fill=0)

    # Display the first few hours of weather data
    draw.text((10,40),  'Messwert', font=font, fill=0)
    draw.text((10,140),  'Temperatur 2m', font=font, fill=0)
    draw.text((10,180),  'Temp. gefühlt', font=font, fill=0)
    draw.text((10,220), 'Luftfeuchte', font=font, fill=0)
    draw.text((10,260), 'Niederschlag', font=font, fill=0)
    draw.text((10,300), 'Probability', font=font, fill=0)
    draw.text((10,340), 'UV-Index', font=font, fill=0)
    
    draw.text((250,40),  'Einheit', font=font, fill=0)
    draw.text((250,140),  '[°C]', font=font, fill=0)
    draw.text((250,180),  '[°C]', font=font, fill=0)
    draw.text((250,220), '[%]', font=font, fill=0)
    draw.text((250,260), '[mm]', font=font, fill=0)
    draw.text((250,300), '[%]', font=font, fill=0)
    draw.text((250,340), '[-]', font=font, fill=0)
    
    x_offset = 375
    #hourly data
    for hour_offset in range(4):
        y_offset = 75
        hour = hour_now + timedelta(hours=hour_offset)
        if hour in hourly_data.index:
            row = hourly_data.loc  [hour]
            draw.text((x_offset,40), f"{hour.strftime('%H:%M')}", font=font, fill=0)
            image.paste(icons [hour_offset], (x_offset + 10, y_offset))
            y_offset = 140
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
            

    #daily data
    daily_data = weather.get_weather_daily()
    
    draw.text((10,410), 'Temp min/max', font=font_small, fill=0)
    draw.text((10,430), 'N-Summe', font=font_small, fill=0)
    draw.text((10,450), 'Beschreibung', font=font_small , fill=0)

    x_offset = 180
    for index in daily_data.index:
        y_offset = 390
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
    print('birthdays: ', birthdays)
    if birthdays:
        x_offset = 425
        y_offset = 390
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
