from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)


def get_coordinates(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru", "format": "json"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("results"):
            return None
        result = data["results"][0]
        return {
            "name": result["name"],
            "country": result.get("country", ""),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        }
    except requests.RequestException:
        return None


def get_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
        }
    except requests.RequestException:
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def weather():
    city = request.form.get("city", "").strip()

    if not city:
        return render_template("result.html", error="Введите название города")

    location = get_coordinates(city)
    if not location:
        return render_template(
            "result.html",
            error=f"Город «{city}» не найден. Попробуйте другое название.",
        )

    weather_data = get_weather(location["latitude"], location["longitude"])
    if not weather_data:
        return render_template(
            "result.html",
            error="Не удалось получить данные о погоде. Попробуйте позже.",
        )

    request_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    return render_template(
        "result.html",
        city=location["name"],
        country=location["country"],
        temperature=weather_data["temperature"],
        wind_speed=weather_data["wind_speed"],
        humidity=weather_data["humidity"],
        request_time=request_time,
    )


if __name__ == "__main__":
    app.run(debug=True)