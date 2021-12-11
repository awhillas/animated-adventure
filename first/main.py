import argparse
import sys

from loguru import logger

# See: https://github.com/Delgan/loguru
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

def main(config):
    logger.debug("Lets get this party started {}!", config)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to config file")
    args = parser.parse_args()

    main(**vars(args))

