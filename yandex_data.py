import requests
import bs4
import csv
import logging
import collections

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('run')

ParseResult = collections.namedtuple(
    'ParseResult',
    (

        'name',
        'detail',
        'price',
        'rating',
        'num_rating',
    )
)

HEADERS = (

    'name',
    'detail',
    'price',
    'rating',
    'num_rating',

)

URL_YANDEX = "https://market.yandex.ru/catalog--konstruktory-v-rostove-na-donu/59749/list?cpa=0&hid=10470548&glfilter=7893318%3A3732937&onstock=1&local-offers-first=0&viewtype=grid"
DRIVERS = {
    URL_YANDEX: (
        # container
        ('article._1O1OnAPlSR._29bSn5MwO8.cia-vs.cia-cs', None),
        # name
        ('a._27nuSZ19h7.wwZc93J2Ao.cia-cs', 'title'),
        # detail
        ('a._27nuSZ19h7.wwZc93J2Ao.cia-cs', 'href'),
        # price
        ('div._3NaXxl-HYN._3f2ZtYT7NH._1f_YBwo4nE', 'span'),
        # rating
        ('span._3nFvoU2Uov', None),
        # num_rating
        ('span.KdrkCVDrVm', None),

    )
}


class Client:

    def __init__(self):
        self.result = []
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Accept-Language': 'ru',
        }

    def load_page(self, url, page: int = None):
        res = self.session.get(url=url)
        print(res)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str, path_container, path_name_block, path_detail_block, path_price_block,
                   path_rating_block, path_num_rating_block):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select(path_container)
        logger.info(container)

        for block in container:
            self.parse_block(block=block,
                             path_name_block=path_name_block,
                             path_detail_block=path_detail_block,
                             path_price_block=path_price_block,
                             path_rating_block=path_rating_block,
                             path_num_rating_block=path_num_rating_block,

                             )

    def parse_block(self, block, path_name_block, path_detail_block, path_price_block, path_rating_block,
                    path_num_rating_block):
        logger.info(block)
        logger.info('=' * 100)

        name_block = block.select_one(path_name_block)

        detail_block = block.select_one(path_detail_block)

        price_block = block.select_one(path_price_block)

        rating_block = block.select_one(path_rating_block)

        num_rating_block = block.select_one(path_num_rating_block)

        element_block = [name_block, detail_block, price_block, rating_block, num_rating_block]

        for element in element_block:
            if not element:
                logger.error('no data')
                return

        for i in DRIVERS.values():
            name = name_block.get(i[1][1])
            detail = detail_block.get(i[2][1])
            price = price_block.find(i[3][1]).text
            rating = rating_block.text
            num_rating = num_rating_block.text

        heads = [name, detail, price, rating, num_rating]
        for head in heads:
            if not head:
                logger.error('no data')
                return

        self.result.append(ParseResult(
            name=name,
            detail=detail,
            price=price,
            rating=rating,
            num_rating=num_rating,

        ))

        logger.debug('%s , %s , %s, %s, %s', name, detail, price, rating, num_rating)
        logger.debug('-' * 100)

    def save(self, path):

        with open(path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self, url):
        text = self.load_page(url)
        path_container, path_name_block, path_detail_block, path_price_block, path_rating_block, path_num_rating_block = (
        (DRIVERS.get(url)[i][0] for i in range(6)))
        self.parse_page(
            text,
            path_container,
            path_name_block,
            path_detail_block,
            path_price_block,
            path_rating_block,
            path_num_rating_block,
        )
        logger.info(f'there are {len(self.result)}')

        self.save(path='data.csv')


if __name__ == '__main__':
    parser = Client()
    parser.parse_page(text='lxml',
                      path_container=DRIVERS[URL_YANDEX][0][0],
                      path_name_block=DRIVERS[URL_YANDEX][1][0],
                      path_detail_block=DRIVERS[URL_YANDEX][2][0],
                      path_price_block=DRIVERS[URL_YANDEX][3][0],
                      path_rating_block=DRIVERS[URL_YANDEX][4][0],
                      path_num_rating_block=DRIVERS[URL_YANDEX][5][0]
                      )
    parser.run(URL_YANDEX)

'''
    for i in range (len(DRIVERS[URL_YANDEX])):
        print (DRIVERS[URL_YANDEX][i])
'''
