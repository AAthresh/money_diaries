import re
import inflect
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json


class Diary:
    """
    This is the parser class with methods
    """

    def __init__(self):
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
        self.base_url = 'https://www.refinery29.com'
        self.links = []

    def get_links(self):
        """

        :return:
        """
        return self.links

    def set_links(self, links):
        """

        :param links:
        :return:
        """
        self.links = links

    def link_grabber(self, url=None):
        """

        :return:
        """

        request_url = ''.join([self.base_url, url]) if url else ''.join([self.base_url, '/en-us/money-diary'])
        req = requests.get(request_url, self.headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        for link in soup.find_all(href=True):
            link_href = link['href']
            pattern = r'/en-us/[a-z-]*money-diary.*'
            result = re.match(pattern, link_href)
            if result:
                if 'page' in result[0]:
                    self.link_grabber(url=link_href)
                else:
                    self.links.append(link_href)

    def diary_grabber(self):
        """
        :return:
        """
        final_diary = {}
        for diary_link in self.links:
            request_url = ''.join([self.base_url, diary_link])

            req = requests.get(request_url, self.headers)
            soup = BeautifulSoup(req.content, 'html.parser')

            divs = soup.find_all('div', {'class': 'section-text'})

            try:
                # Extract basic info
                occupation_index = 0
                day_one_index = 0
                for i, d in enumerate(divs):
                    if 'occupation' or 'industry' in d.text.lower():
                        occupation_index = i
                    elif 'day one' in d.text.lower():
                        day_one_index = i
                        break

                basic_divs = divs[occupation_index: day_one_index]

                def parser(lst):
                    key = value = None
                    result = {}

                    for elem in lst:

                        if isinstance(elem, Tag) and elem.can_be_empty_element:
                            continue

                        if isinstance(elem, Tag):
                            key = elem.text.replace(':', '').strip()

                        if isinstance(elem, NavigableString):
                            value = str(elem).strip()

                        result[key] = value
                    return result

                basic_info = {}
                for div in basic_divs:
                    basic_info.update(parser(div))

                # Extract the diaries
                diary_divs = divs[day_one_index:]
                diaries = {}
                converter = inflect.engine()
                index = 1

                for i, d in enumerate(diary_divs):
                    start_index = f'day {converter.number_to_words(index)}'
                    end_index = 'daily total'

                    if end_index in d.text.lower():
                        diaries[start_index][end_index] = d.text.lower().replace('daily total:', '').strip()
                        index += 1

                    if start_index in d.text.lower():
                        diaries[start_index] = {}

                    else:
                        pattern = r'(\d{1,2}(:\d{1,2})? (a\.m|p\.m)\.?)'
                        result = re.match(pattern, d.text.lower())
                        if result:
                            key = f'{result[0]}'
                            diaries[start_index][key] = d.text.lower().replace(result[0], '').strip()

                basic_info.update(diaries)
                final_diary[diary_link.replace('/en-us/', '')] = basic_info
            except:
                print(f'Error parsing {diary_link}')
                continue

        with open('result.json', 'w') as fp:
            json.dump(final_diary, fp)


def main():
    """

    :return:
    """
    diary = Diary()
    diary.link_grabber()

    diary_links = diary.get_links()
    print(f'Total number of diaries to parse {len(diary_links)}')

    diary.diary_grabber()


if __name__ == '__main__':
    main()
