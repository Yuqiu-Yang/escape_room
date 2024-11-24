import os 
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from escape_room.auth import login_required
from escape_room.db import get_db

from .room import Game
from .reader import CampaignReader

from typing import Any, Optional

bp = Blueprint('puzzle', __name__)

EPOCH: datetime.datetime = datetime.datetime(1970, 1, 1)
START_TIME: datetime.datetime = EPOCH
GAME: Optional[Game] = None
NOTES: list = []
CURRENT_PUZZLE: Optional[str] = None

@bp.route("/")
def index():
    """Method to render homepage."""
    global GAME
    GAME = CampaignReader(os.path.join(os.path.dirname(__file__),"./campaigns/game.json")).get_game_from_campaign()
    return render_template(
        "puzzle/index.html", title=GAME.title, text=GAME.text, images=GAME.images,
    )


def get_puzzle(puzzle_id: str) -> Any:
    """Method to get the puzzle.

    :param puzzle_id: ID of the puzzle.
    """
    global START_TIME
    if puzzle_id == CampaignReader.STARTING_PUZZLE_KEY and START_TIME == EPOCH:
        START_TIME = datetime.datetime.now()

    global NOTES
    global CURRENT_PUZZLE
    CURRENT_PUZZLE = puzzle_id
    if GAME and puzzle_id in GAME.puzzles:
        puzzle = GAME.puzzles[puzzle_id]
        return render_template(
            "puzzle/puzzle.html",
            title=puzzle.title,
            text=puzzle.text,
            images=puzzle.images,
            hints=puzzle.hints,
        )
    else:
        return redirect("/404")


def submit_answer(puzzle_id: str) -> Any:
    """Method to submit answer to the puzzle.

    :param puzzle_id: ID of the puzzle.
    """
    if GAME and puzzle_id in GAME.puzzles:
        puzzle = GAME.puzzles[puzzle_id]
        if request.form["answer"].lower() == puzzle.answer.lower():
            NOTES.append("{}: {}".format(puzzle.text, request.form["answer"]))
            if puzzle.next_puzzle == CampaignReader.FINAL_PUZZLE_KEY:
                seconds = int((datetime.datetime.now() - START_TIME).total_seconds())
                minutes = seconds // 60
                seconds = seconds % 60
                hours = minutes // 60
                minutes = minutes % 60
                return render_template(
                    "puzzle/winner.html",
                    timetaken=f"{hours} hours {minutes} minutes {seconds} seconds",
                )
            else:
                return redirect(f"/puzzle/{puzzle.next_puzzle}")
        else:
            return render_template(
                "puzzle/puzzle.html",
                title=puzzle.title,
                text=puzzle.text,
                images=puzzle.images,
                hints=puzzle.hints,
            )
    else:
        return redirect("/404")


@bp.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if GAME:
        return render_template("puzzle/notes.html",
                               notes=NOTES,
                               current_puzzle="/puzzle/"+CURRENT_PUZZLE)

@bp.route("/puzzle/<puzzle_id>", methods=["GET", "POST"])
@login_required
def riddler(puzzle_id: str) -> Any:
    """Method to render the puzzles."""
    if request.method == "GET":
        return get_puzzle(puzzle_id)
    elif request.method == "POST":
        return submit_answer(puzzle_id)




