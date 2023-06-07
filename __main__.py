import logging
import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TextIO

import click
import lxml.etree
import pyquery
import telegram_notifier as tn
import yaml

logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)
LOGGER = logging.getLogger()

DEBUG_MESSAGE = 'Nothing happened, but I\'m still checking'

search_query = Mapping[str, str]


@dataclass
class SearchResult:
    selector: str
    action: str
    item: str


def check_url(url: str, search_queries: list[search_query]) -> list[SearchResult]:
    result = []
    d = pyquery.PyQuery(url=url)
    for query in search_queries:
        assert 'contains' in query or 'not_contains' in query, 'Query must have at least one of `contains` or `not_contains'
        html = lxml.etree.tostring(d(query['selector'])[0]).decode()
        if contains := query.get('contains'):
            if query['contains'] in html:
                result.append(SearchResult(query['selector'], 'contains', contains))
        if not_contains := query.get(''):
            if query['contains'] not in html:
                result.append(SearchResult(query['selector'], 'does not contain', not_contains))
    return result


@click.command()
@click.argument('config_file', type=click.File('r'))
def main(config_file: TextIO):
    LOGGER.info('Loading config file')
    config = yaml.safe_load(config_file)

    LOGGER.info('Setting telegram bot options')
    tn.set_config_options(chat_id=config['chat_id'], token=os.environ['BOT_TOKEN'])

    url = config['url']
    poll_interval = config['poll_interval']
    search_queries = config['search_queries']
    debug = config.get('debug', False)


    if config.get('init_notification'):
        LOGGER.info('Sending startup notification')
        tn.send_message(f'Started monitoring\n{url}')

    try:
        LOGGER.info('Start checking')
        while True:
            if results := check_url(url, search_queries):
                for result in results:
                    message = f'Selector\n> {result.selector}\n{result.action}\n> {result.item}\non url\n> {url}'
                    LOGGER.info(message)
                    tn.send_message(message)
            elif debug:
                tn.send_message(DEBUG_MESSAGE)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        tn.send_message(f'Stopped monitoring {url}')
        LOGGER.info('Shutting down')

if __name__ == '__main__':
    main()  # type: ignore
