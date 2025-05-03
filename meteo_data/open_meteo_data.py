import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from PIL import Image


class OpenMeteoWeather:
    def __init__(self, latitude, longitude):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

        # Dictionary to store weather code translations
        self.weather_code_translations = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Drizzle: Light intensity",
            53: "Drizzle: Moderate intensity",
            55: "Drizzle: Dense intensity",
            56: "Freezing Drizzle: Light intensity",
            57: "Freezing Drizzle: Dense intensity",
            61: "Rain: Slight intensity",
            63: "Rain: Moderate intensity",
            65: "Rain: Heavy intensity",
            66: "Freezing Rain: Light intensity",
            67: "Freezing Rain: Heavy intensity",
            71: "Snow fall: Slight intensity",
            73: "Snow fall: Moderate intensity",
            75: "Snow fall: Heavy intensity",
            77: "Snow grains",
            80: "Rain showers: Slight intensity",
            81: "Rain showers: Moderate intensity",
            82: "Rain showers: Violent intensity",
            85: "Snow showers: Slight intensity",
            86: "Snow showers: Heavy intensity",
            95: "Thunderstorm: Slight or moderate",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }

        # Dictionary to map is_day and weather descriptions to icons
        self.weather_icons = {
            ((0), True): "01d",
            ((0), False): "01n",
            ((1), True): "02d",
            ((1), False): "02n",
            ((2), True): "03d",
            ((2), False): "03n",
            ((3), True): "04d",
            ((3), False): "04n",
            ((80,81,82), True): "09d",
            ((80,81,82), False): "09n",
            ((61,63,65), True): "10d",
            ((61,63,65), False): "10n",
            ((95,96,99), True): "11d",
            ((95,96,99), False): "11n",
            ((71,73,75,77,66,67), True): "13d",
            ((71,73,75,77,66,67), False): "13n",
            ((45,48,51,53,55,56,57), True): "50d",
            ((45,48,51,53,55,56,57), False): "50n"
        }

        self.url = "https://api.open-meteo.com/v1/forecast"

        self.latitude = latitude
        self.longitude = longitude

    def get_weather_hourly(self):
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m",
                        "precipitation", "precipitation_probability", "uv_index", "weather_code", "is_day"],
            "forecast_days": 1,
        }
        responses = self.openmeteo.weather_api(self.url, params=params)

        response = responses[0]
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "temperature_apparent": hourly.Variables(1).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(2).ValuesAsNumpy(),
            "precipitation": hourly.Variables(3).ValuesAsNumpy(),
            "precipitation_probability": hourly.Variables(4).ValuesAsNumpy(),
            "uv_index": hourly.Variables(5).ValuesAsNumpy(),
            "weather_code": hourly.Variables(6).ValuesAsNumpy(),
            "is_day": hourly.Variables(7).ValuesAsNumpy()
        }

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        hourly_dataframe.set_index('date', inplace=True)
        return hourly_dataframe

    def get_weather_daily(self):
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "daily": ["temperature_2m_min", "temperature_2m_max", "weather_code", "precipitation_sum"],
            "forecast_days": 3,
        }
        responses = self.openmeteo.weather_api(self.url, params=params)

        response = responses[0]
        daily = response.Daily()
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ),
            "temperature_2m_min": daily.Variables(0).ValuesAsNumpy(),
            "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
            "weather_code": daily.Variables(2).ValuesAsNumpy(),
            "precipitation_sum": daily.Variables(3).ValuesAsNumpy(),
        }

        daily_dataframe = pd.DataFrame(data=daily_data)
        daily_dataframe.set_index('date', inplace=True)
        return daily_dataframe

    def get_icon(self, weather_code, is_day):
        iconnr = None

        for key, value in self.weather_icons.items():            
            if (isinstance(key[0], tuple)):
                # Check if weather_code is in the tuple
                if weather_code in key[0] and is_day == key[1]:
                    iconnr = value
                    break
            else:
                # Check if weather_code is equal to the single value
                if weather_code == key[0] and is_day == key[1]:
                    iconnr = value
                    break
        return iconnr

    def get_icon_url(self, weather_code, is_day):
        iconnr = self.get_icon(weather_code, is_day)
        if iconnr:
            return f"https://openweathermap.org/img/wn/{iconnr}@2x.png"
        return None

    def images_of_weather_icons(self, path_to_icon_folder, weather_dataframe):
        img_list = []
        for i, (index, row) in enumerate(weather_dataframe.iterrows()):
            weather_code = row['weather_code']
            is_day = row['is_day']
            icon_name = self.get_icon(weather_code, is_day)
            image_path = ''.join([path_to_icon_folder,icon_name,'.bmp'])
            image = Image.open(image_path)
            image = image.resize((50,50))
            img_list.append(image)

        return img_list

