# coding:utf-8

import gamelocker
import sys, traceback, time, requests

from app.app import app
from app.database import db
from app.models import MHeroes, MItems, Matches, Players, Participants, Rosters, StatHeroes, StatHeroesDuration, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type, analyze_telemetry

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from requests.exceptions import HTTPError
from datetime import datetime, date, timedelta, timezone
from time import sleep

"""
calcurate average cs
"""

def main():
    

    return


main()