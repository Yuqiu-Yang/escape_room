import sqlite3
import os 
import pickle
from datetime import datetime

import click
from flask import current_app, g
from .reader import CampaignReader



def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_game():
    GAME = CampaignReader(os.path.join(os.path.dirname(__file__),"./campaigns/game.json")).get_game_from_campaign()
    with open(os.path.join(os.path.dirname(__file__), '../instance/game.pickle'), 'wb') as handle:
        pickle.dump(GAME, handle, protocol=pickle.HIGHEST_PROTOCOL)
    

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('init-game')
def init_game_command():
    """Clear the existing game and create new game."""
    init_game()
    click.echo('Initialized the game.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_game_command)