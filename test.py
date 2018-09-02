from app.app import app
from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import gamelocker
"""
api = gamelocker.Vainglory(app.config['API_KEY'])

# Reference: https://developer.vainglorygame.com/docs#get-a-collection-of-players
args = {'filter[playerNames]': 'Kootam'}
data = api.players(args, 'ea')
"""

api = gamelocker.Gamelocker(app.config['API_KEY']).Vainglory()
params = {
    'filter[gameMode]': 'ranked',
    'filter[playerNames]': 'syatin'
}
data = api.matches(params, region='ea')

print(data)