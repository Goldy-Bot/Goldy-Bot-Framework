import sys; sys.path.insert(0, '..')

import os
from GoldyBot.info import VERSION

os.system(
    f"docker build -t devgoldy/goldybot:{VERSION} ."
)

os.system(
    "docker build -t devgoldy/goldybot:latest ."
)