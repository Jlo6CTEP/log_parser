import asyncio
from dataclasses import dataclass
from math import nan
from typing import List, Type

import httpx as httpx

from consumers.basic_consumer import SinkConsumer
from events.base_event import BaseEvent
from events.spacetab_event import SpaceTabLogEvent
from logging_facility import logger

USER_BY_NAME_URL = "https://api.vimeworld.ru/user/name/{id}"
USER_STATS = "https://api.vimeworld.ru/user/{id}/stats"
USER_FRIENDS = "https://api.vimeworld.ru/user/{id}/friends"


@dataclass
class SpaceTabEventConsumer(SinkConsumer):

    def __init__(self, events_to_respond: List[Type[BaseEvent]]):
        super().__init__(events_to_respond)

    async def process(self, item: SpaceTabLogEvent) -> None:

        logger.info(f"Tab event {item.nicknames_list}")

        client = httpx.AsyncClient(
            headers={'Access-Token': 'DBNu2un2V2NWBPvHasoe7Q5GrevwPLl'})

        # first get user profiles by their names
        user_list = (await client.get(
            USER_BY_NAME_URL.format(id=','.join(item.nicknames_list))
        )).json()

        # prepare request to get their stats
        user_stats_coro = [client.get(
            USER_STATS.format(id=x['id']),
            params={'games': 'EGGWARS'}
        ) for x in user_list]

        # and friends

        user_friends_coro = [client.get(
            USER_FRIENDS.format(id=x['id'])
        ) for x in user_list]

        # send all the requests simultaneously
        result = await asyncio.gather(
            *user_friends_coro,
            *user_stats_coro
        )

        users_friends = [
            [friend['username'] for friend in player.json()['friends']]
            for player in result[:len(result) // 2]
        ]
        users_stats = [
            x.json()['stats']['EGGWARS']['global']
            for x in result[len(result) // 2:]
        ]
        current_party_id = 0
        teams = {user['username']: set() for user in user_list}
        for user, user_friends in zip(teams.keys(), users_friends):
            for friend in user_friends:
                if friend in teams and (
                        len(teams[friend] - teams[user]) > 0
                        or not teams[user]
                ):
                    teams[friend].add(current_party_id)
                    teams[user].add(current_party_id)
            current_party_id += 1

        # This looks like junk though

        report_dict = [
            {"name": user['username'],
             "Party IDs": ' '.join(map(str, party)),
             "guild": user['guild']['name'] if user['guild'] else "",
             "level": user['level'],
             "games": stat['games'],
             "W/R": stat['wins']/stat['games'] if stat['games'] else nan,
             "kills": stat['kills'],
             "K/D": stat['kills']/(stat['deaths'] if stat['deaths'] else 1),
             "Mobs": stat['monsters']/(stat['games'] if stat['games'] else 1),
            }
            for user, stat, party in zip(
                user_list, users_stats, teams.values())
        ]

        a = [
            print(''.join([x.ljust(20) for x in report_dict[0].keys()])),
            [print(''.join([str(x).ljust(20) for x in f.values()])) for f in report_dict]
        ]
        print('\n')
        await client.aclose()

