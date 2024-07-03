from .models import Games
from celery import shared_task
import requests
from collections import defaultdict
from .models import Games, StreamSniper, Score
from django.db.models import F
import os


def get_quin_team(match):
    for player in match["info"]["participants"]:
        if player["riotIdGameName"] == "ABOBA" and player["riotIdTagline"] == "YAP":
            return player["teamId"]


def get_winning_team(match):
    if match["info"]["teams"][0]["win"]:
        return match["info"]["teams"][0]["teamId"]
    else:
        return match["info"]["teams"][1]["teamId"]


@shared_task
def fetch():

    headers = {"X-Riot-Token": os.environ.get("RIOT_API_KEY")}
    account_ABOBA = (
        "https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/ABOBA/YAP"
    )
    quin_ABOBA_puuid = requests.get(account_ABOBA, headers=headers).json()["puuid"]
    matches_ABOBA_url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{quin_ABOBA_puuid}/ids?start=0&count=100"
    matches_ABOBA = requests.get(matches_ABOBA_url, headers=headers).json()

    saved_matches = list(Games.objects.all().values_list("game_id", flat=True))
    new_matches = [match for match in matches_ABOBA if match not in saved_matches]

    if len(new_matches) == 0:
        return None

    match_url = "https://sea.api.riotgames.com/lol/match/v5/matches/"
    matches_info = {}
    for match in new_matches:
        matches_info[match] = requests.get(match_url + match, headers=headers).json()

    def default_value():
        return {
            "win_with_quin": 0,
            "loss_with_quin": 0,
            "win_against_quin": 0,
            "loss_against_quin": 0,
            "total": 0,
        }

    data = defaultdict(default_value)

    for match in matches_info.values():
        winning_team = get_winning_team(match)
        quin_team = get_quin_team(match)
        for player in match["info"]["participants"]:
            if player["teamId"] == winning_team and player["teamId"] == quin_team:
                data[(player["riotIdGameName"], player["riotIdTagline"])][
                    "win_with_quin"
                ] += 1
            if player["teamId"] != winning_team and player["teamId"] == quin_team:
                data[(player["riotIdGameName"], player["riotIdTagline"])][
                    "loss_with_quin"
                ] += 1
            if player["teamId"] == winning_team and player["teamId"] != quin_team:
                data[(player["riotIdGameName"], player["riotIdTagline"])][
                    "win_against_quin"
                ] += 1
            if player["teamId"] != winning_team and player["teamId"] != quin_team:
                data[(player["riotIdGameName"], player["riotIdTagline"])][
                    "loss_against_quin"
                ] += 1
            data[(player["riotIdGameName"], player["riotIdTagline"])]["total"] += 1

    del data[("ABOBA", "YAP")]

    for match in new_matches:
        Games.objects.create(game_id=match)

    for player, stats in data.items():
        sniper, _ = StreamSniper.objects.get_or_create(
            riotIdGameName=player[0], riotIdTagline=player[1]
        )
        win_with_quin = stats["win_with_quin"]
        loss_with_quin = stats["loss_with_quin"]
        win_against_quin = stats["win_against_quin"]
        loss_against_quin = stats["loss_against_quin"]
        total_games = stats["total"]
        Score.objects.update_or_create(
            streamsniper=sniper,
            defaults={
                "win_with_quin": F("win_with_quin") + win_with_quin,
                "loss_with_quin": F("loss_with_quin") + loss_with_quin,
                "win_against_quin": F("win_against_quin") + win_against_quin,
                "loss_against_quin": F("loss_against_quin") + loss_against_quin,
                "total_games": F("total_games") + total_games,
            },
            create_defaults={
                "streamsniper": sniper,
                "win_with_quin": win_with_quin,
                "loss_with_quin": loss_with_quin,
                "win_against_quin": win_against_quin,
                "loss_against_quin": loss_against_quin,
                "total_games": win_with_quin
                + loss_with_quin
                + win_against_quin
                + loss_against_quin,
            },
        )
