from json import loads
from os import path
from typing import Any, Dict
from uuid import uuid4

import jsonschema

from .room import Game, Scene, Puzzle


class CampaignReader:
    """Class to validate and extract game details from JSON campaign."""

    STARTING_SCENE_KEY: str="1"
    FINAL_SCENE_KEY: str="end"

    # STARTING_PUZZLE_KEY: str = "1"
    # FINAL_PUZZLE_KEY: str = "end"

    # Common keys.
    TITLE_KEY: str = "title"
    TEXT_KEY: str = "text"
    IMAGES_KEY: str = "images"

    # Story keys.
    STORY_KEY: str = "story"

    # List of scenes key 
    SCENES_KEY: str = "scenes"

    # List of puzzles key
    PUZZLES_KEY: str = "puzzles"

    # Key in each puzzles.
    PUZZLE_HINTS_KEY: str = "hints"
    PUZZLE_ANSWER_KEY: str = "answer"
    PUZZLE_CLUES_KEY: str = "clues"
    PUZZLE_IS_END_SCENE_KEY: str = "is_end_scene"


    def __init__(self, campaign_file: str) -> None:
        """Constructor.

        :param campaign_file: Absolute path to JSON file with campaign information.
        :type str:
        :raises: FileNotFoundError if invalid path is provided in |campaign_file|.
        :raises: JSONDecodeError if the provided |campaign_file| is not JSON file.
        :raises: ValidationError if campaign doesn't conform to `config.schema`.
        """
        # Read campaign JSON.
        self.campaign: Dict[str, Any] = self._load_file(campaign_file)

        # Read config.schema for validation.
        here = path.abspath(path.dirname(__file__))
        self.schema = self._load_file(path.join(here, "config.schema"))

    def _load_file(self, file_path: str) -> Dict[str, Any]:
        """Method to load JSON file and return a dictionary.

        :param file_path: JSON file path.
        :type str:
        """
        with open(file_path, "r") as f:
            return loads(f.read())

    def validate(self) -> None:
        """Method to validate the provided campaign.

        :raises: ValidationError if campaign doesn't conform to `config.schema`.
        """
        jsonschema.validate(self.campaign, self.schema)

    def get_game_from_campaign(self) -> Game:
        """Method to procure game setup from campaign."""

        # Dictionary with scenes
        scenes: Dict[str, Any] = {}

        # Always begin with 1 as the scene ID and move through the chain.
        next_key = CampaignReader.STARTING_SCENE_KEY
        # Keep track of total scenes to mark end key appropriately.
        total_steps = len(self.campaign[CampaignReader.SCENES_KEY])  
        # Iterate through scene list and create chained scene dictionary.
        #
        # "1": <FirstScene> where <FirstScene>.next_scene points to the scene
        # to go to and so on and so forth. With last scene having next_scene id
        # set to "end"
        for i, scene in enumerate(self.campaign[CampaignReader.SCENES_KEY]):
            key = next_key
            next_key = str(uuid4())
            
            puzzles: Dict[str, Any] = {}
            for j, puzzle in enumerate(scene[CampaignReader.PUZZLES_KEY]):
                puzzles[str(j)] = Puzzle(
                    title=puzzle[CampaignReader.TITLE_KEY],
                    text=puzzle[CampaignReader.TEXT_KEY],
                    images=puzzle[CampaignReader.IMAGES_KEY],
                    hints=puzzle[CampaignReader.PUZZLE_HINTS_KEY],
                    answer=puzzle[CampaignReader.PUZZLE_ANSWER_KEY],
                    clues=puzzle[CampaignReader.PUZZLE_HINTS_KEY],
                    is_end_scene=puzzle[CampaignReader.PUZZLE_IS_END_SCENE_KEY]
                ) 

            scenes[key] = Scene(
                title=scene[CampaignReader.TITLE_KEY],
                text=scene[CampaignReader.TEXT_KEY],
                images=scene[CampaignReader.IMAGES_KEY],
                puzzles=puzzles,
                next_scene=CampaignReader.FINAL_SCENE_KEY
                if i == total_steps - 1
                else next_key,
            )

        return Game(
            title=self.campaign[CampaignReader.STORY_KEY][CampaignReader.TITLE_KEY],
            text=self.campaign[CampaignReader.STORY_KEY][CampaignReader.TEXT_KEY],
            images=self.campaign[CampaignReader.STORY_KEY][CampaignReader.IMAGES_KEY],
            scenes=scenes
        )


        # # Dictionary with puzzles.
        # puzzles: Dict[str, Any] = {}

        # # Always begin with 1 as the puzzle ID and move through the chain.
        # next_key = CampaignReader.STARTING_PUZZLE_KEY
        # # Keep track of total puzzles to mark end key appropriately.
        # total_steps = len(self.campaign[CampaignReader.PUZZLES_KEY])

        # # Iterate through puzzle list and create chained puzzle dictionary.
        # #
        # # "1": <FirstPuzzle> where <FirstPuzzle>.next_puzzle points to the puzzle
        # # to go to and so on and so forth. With last puzzle having next_puzzle id
        # # set to "end"
        # for i, puzzle in enumerate(self.campaign[CampaignReader.PUZZLES_KEY]):
        #     key = next_key
        #     next_key = str(uuid4())
        #     puzzles[key] = Puzzle(
        #         title=puzzle[CampaignReader.TITLE_KEY],
        #         text=puzzle[CampaignReader.TEXT_KEY],
        #         images=puzzle[CampaignReader.IMAGES_KEY],
        #         hints=puzzle[CampaignReader.PUZZLE_HINTS_KEY],
        #         answer=puzzle[CampaignReader.PUZZLE_ANSWER_KEY],
        #         next_puzzle=CampaignReader.FINAL_PUZZLE_KEY
        #         if i == total_steps - 1
        #         else next_key,
        #     )

        # return Game(
        #     title=self.campaign[CampaignReader.STORY_KEY][CampaignReader.TITLE_KEY],
        #     text=self.campaign[CampaignReader.STORY_KEY][CampaignReader.TEXT_KEY],
        #     images=self.campaign[CampaignReader.STORY_KEY][CampaignReader.IMAGES_KEY],
        #     scenes=scenes
        #     # puzzles=puzzles,
        # )