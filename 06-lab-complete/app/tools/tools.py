import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import search_flights as sf
import hotel as ht
import get_weather as gw
import calculate_total_price as ctp

SIMULATE_ERROR = False

def search_flights(departure_city: str, destination_city: str, departure_date: str) -> list:
    return sf.search_flights(departure_city, destination_city, departure_date)

def hotel(destination_city: str, rate: int) -> list:
    return ht.hotel(destination_city, rate)

def get_weather(destination_city: str, departure_date: str) -> dict:
    gw.SIMULATE_ERROR = SIMULATE_ERROR
    return gw.get_weather(destination_city, departure_date)

def calculate_total_price(flight_id: str, hotel_id: str) -> dict:
    return ctp.calculate_total_price(flight_id, hotel_id)

TOOLS = [
    sf.SCHEMA,
    ht.SCHEMA,
    gw.SCHEMA,
    ctp.SCHEMA
]
