import os 
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

bp = Blueprint('scene', __name__)

EPOCH: datetime.datetime = datetime.datetime(1970, 1, 1)
START_TIME: datetime.datetime = EPOCH
GAME: Optional[Game] = None

@bp.route("/")
def index():
    """Method to render homepage."""
    global GAME
    GAME = CampaignReader(os.path.join(os.path.dirname(__file__),"./campaigns/game.json")).get_game_from_campaign()
    if "puzzles_seen_str" not in session:
        session["puzzles_seen_str"] = "<eos>"
        session['current_puzzle_id'] = "1"
    return render_template(
        "scene/index.html", title=GAME.title, text=GAME.text, images=GAME.images,
    )


def get_scene(scene_id: str) -> Any:
    """Method to get the scene.

    :param puzzle_id: ID of the scene.
    """
    global START_TIME
    if scene_id == CampaignReader.STARTING_SCENE_KEY and START_TIME == EPOCH:
        START_TIME = datetime.datetime.now()
    session['current_puzzle_id'] = scene_id
    if GAME and scene_id in GAME.scenes:
        scene = GAME.scenes[scene_id]
        intermediate_puzzle_ids = [str(i) for i in range(len(scene.puzzles)-1)]
        final_puzzle_id = str(len(scene.puzzles)-1)

        return render_template(
            "scene/scene.html",
            scene_title=scene.title,
            scene_text=scene.text,
            scene_images=scene.images,
            puzzles=scene.puzzles,
            intermediate_puzzle_ids=intermediate_puzzle_ids,
            final_puzzle_id=final_puzzle_id
        )
    else:
        return redirect("/404")


def submit_answer(scene_id: str) -> Any:
    """Method to submit answer to the puzzle.

    :param puzzle_id: ID of the puzzle.
    """
    if GAME and puzzle_id in GAME.scenes:
        scene = GAME.scenes[puzzle_id]

        data = request.get_json()
        section_id = data.get('section_id')
        user_input = data.get('user_input', '').strip()

        solutions = [a.strip().lower() for a in scene.answer]
        solutions = [a for a in solutions if a != ""]


        answers = request.form["answer"].split(";")
        answers = [a.strip().lower() for a in answers]
        answers = [a for a in answers if a != ""]
        
        if set(answers) == set(solutions):
            if puzzle.text not in session['puzzles_seen_str']:
                session['puzzles_seen_str'] += "<strong>Puzzle:</strong><br>{}<br><strong>Answer:</strong><br>{}<eos>".format(puzzle.text, request.form["answer"])
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


@bp.route("/scene/<scene_id>", methods=["GET", "POST"])
@login_required
def riddler(scene_id: str) -> Any:
    """Method to render the puzzles."""
    if request.method == "GET":
        return get_scene(scene_id)
    elif request.method == "POST":
        return submit_answer(scene_id)
