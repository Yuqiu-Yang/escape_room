import os 
import pickle 
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
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
# GAME: Optional[Game] = None

@bp.route("/")
def index():
    """Method to render homepage."""
    # global GAME
    # GAME = CampaignReader(os.path.join(os.path.dirname(__file__),"./campaigns/game.json")).get_game_from_campaign()
    with open(os.path.join(os.path.dirname(__file__), '../instance/game.pickle'), 'rb') as handle:
         GAME = pickle.load(handle)
    
    db = get_db()
    puzzles_seen_str = (
        get_db()
        .execute(
            "SELECT * FROM temp"
        )
        .fetchone()
    )
    if puzzles_seen_str is None:
        db = get_db()
        db.execute(
            "INSERT INTO temp (id, puzzles_seen_str) VALUES (?, ?)",
            ("1", "<eos>"),
        )
        db.commit()
    if "current_puzzle_id" not in session:
        # session["puzzles_seen_str"] = "<eos>"
        session['current_puzzle_id'] = "1"
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
    session['current_puzzle_id'] = puzzle_id
    with open(os.path.join(os.path.dirname(__file__), '../instance/game.pickle'), 'rb') as handle:
         GAME = pickle.load(handle)
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
    with open(os.path.join(os.path.dirname(__file__), '../instance/game.pickle'), 'rb') as handle:
         GAME = pickle.load(handle)
    if GAME and puzzle_id in GAME.puzzles:
        puzzle = GAME.puzzles[puzzle_id]
        answers = request.form["answer"].split(";")
        answers = [a.strip().lower() for a in answers]
        answers = [a for a in answers if a != ""]
        solutions = [a.strip().lower() for a in puzzle.answer]
        solutions = [a for a in solutions if a != ""]
        if set(answers) == set(solutions):
            db = get_db()
            puzzles_seen_str = (
                get_db()
                .execute(
                    "SELECT * FROM temp"
                )
                .fetchone()
            )
            if puzzle.text not in puzzles_seen_str['puzzles_seen_str']:
                temp_str = puzzles_seen_str['puzzles_seen_str'] + "<strong>Puzzle:</strong><br>{}<br><strong>Answer:</strong><br>{}<eos>".format(puzzle.text, request.form["answer"])
                db = get_db()
                db.execute(
                    "UPDATE temp SET puzzles_seen_str = ? WHERE id = 1", (str(temp_str),)
                )
                db.commit()
            if puzzle.next_puzzle == CampaignReader.FINAL_PUZZLE_KEY:
                seconds = int((datetime.datetime.now() - START_TIME).total_seconds())
                minutes = seconds // 60
                seconds = seconds % 60
                hours = minutes // 60
                minutes = minutes % 60
                timetaken = f"{hours} hours {minutes} minutes {seconds} seconds"

                db = get_db()
                db.execute(
                    "INSERT INTO completions (user_id, start_time, time_taken) VALUES (?, ?, ?)",
                    (g.user["id"], START_TIME.isoformat(), timetaken),
                )
                db.commit()

                return render_template(
                    "puzzle/winner.html",
                    timetaken=timetaken,
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


@bp.route("/puzzle/<puzzle_id>", methods=["GET", "POST"])
@login_required
def riddler(puzzle_id: str) -> Any:
    """Method to render the puzzles."""
    if request.method == "GET":
        return get_puzzle(puzzle_id)
    elif request.method == "POST":
        return submit_answer(puzzle_id)
