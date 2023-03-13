import requests
import unicodedata
import re
import os
from datetime import date, timedelta
from bs4 import BeautifulSoup, Tag

base_url = "https://www.understandingwar.org/backgrounder/"
initial_path = "russia-ukraine-warning-update-initial-russian-offensive-campaign-assessment"
old_path = "russia-ukraine-warning-update-russian-offensive-campaign-assessment"
new_path = "russian-offensive-campaign-assessment"

start_date = date(2022,2,24)
end_date = date(2023,1,25)

default_month_day_format = "%B-%#d"
default_year_month_day_format = "%B-%#d-%Y"

def get_url(curr_date: date):
    if curr_date == date(2022,2,24):
        return f'{base_url}{initial_path}'
    elif curr_date == date(2022,2,25):
        return f'{base_url}{old_path}-{curr_date.strftime(default_year_month_day_format)}'
    elif curr_date < date(2022,2,28):
        return f'{base_url}{old_path}-{curr_date.strftime(default_month_day_format)}'
    elif curr_date == date(2022,2,28):
        return f'{base_url}{new_path}-{curr_date.strftime(default_year_month_day_format)}'
    elif curr_date.year == 2022:
        return f'{base_url}{new_path}-{curr_date.strftime(default_month_day_format)}'
    else:
        return f'{base_url}{new_path}-{curr_date.strftime(default_year_month_day_format)}'


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def get_article(url: str):
    response = requests.get(url)
    return response.text, response.status_code

def retrieve_data(data):
    res = []
    parser = BeautifulSoup(data, 'html.parser')
    text_blocks = parser.find('div', {'class': 'field-type-text-with-summary'}).find('div', {'class': 'field-item even'})
    for block in text_blocks.select('div, p, ul')[2:]:
        res.append(block)
    return res

def parse_blocks(blocks):
    res = []
    for block in blocks:
        data: Tag = block
        text = unicodedata.normalize('NFKD', data.text)

        if not text.strip() or data.find('a') or data.find('img') or data.find('br') or 'Click here' in text or 'https' in text or 'http' in text or 'Note:' in text:
            continue
        else:
            text = text.replace('&nbsp','')
            text = re.sub(r'\[\d+\]', '', text)
            res.append(text)
    return '\n'.join(res)

def write_report_to_file(text, date):
    if(not os.path.exists("isw_reports")):
        os.makedirs("isw_reports")
    with open(f'isw_reports/ISW_{date}.txt', 'w', encoding = "utf-8") as file:
        file.write(text)

def main():
   for date in daterange(start_date,end_date):
      url = get_url(date)
      article, code = get_article(url)
      if code != 200:
          continue
      data = retrieve_data(article)
      text = parse_blocks(data)
      write_report_to_file(text, date.strftime('%Y-%m-%d'))


if __name__ == '__main__':
    main()