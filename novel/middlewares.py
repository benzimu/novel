# -*- coding: utf-8 -*-

import random
import json

from utils.user_agents import agents


class UserAgentMiddleware(object):
    """更换User-Agent"""
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
