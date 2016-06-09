import urllib2
import sys
import os.path

import lxml.html as html
import pandas as pd

reddit_url = 'https://reddit.com'
start_url = 'https://reddit.com/r/jokes'
headers = { 'User-Agent': '/u/Broscious' }
upvote_threshold = 100

def url_open(url):
    req = urllib2.Request(url, headers=headers)
    return urllib2.urlopen(req)

def retrieve_urls():
    root = html.parse(url_open(start_url)).getroot()
    scores = root.xpath('//div[@class="score unvoted"]/text()')
    relative_paths = root.xpath('//a[@class="title may-blank "]/@href')
    absolute_paths = [reddit_url + relative for relative in relative_paths]
    filtered_paths = []
    for url, upvotes in zip(absolute_paths, scores):
        try:
            value = int(upvotes)
        except:
            value = -1
        if value >= upvote_threshold:
            filtered_paths.append(url)
    return filtered_paths

def retrieve_joke(url):
    root = html.parse(url_open(url)).getroot()
    setup = root.xpath('//a[@class="title may-blank "]/text()')[0]
    content = root.xpath('//div[@class="expando expando-uninitialized"]//p/text()')
    return setup, content

def one_line_filter(setup, content):
    for paragraph in content[1:]:
        low_para = paragraph.lower()
        if low_para.startswith('edit:'):
            continue
        else:
            return None

    punchline = content[0]
    if punchline.count('.') > 1:
        return None

    return setup, punchline

def filter_results(urls, results):
    returns = []
    for url, result in zip(urls, results):
        title, content = result
        joke = one_line_filter(title, content)
        if joke is not None:
            returns.append((url, joke[0], joke[1]))
    return returns

def save_results(one_liners, joke_file, url_file):
    used_urls = pd.read_csv(url_file)
    added_urls = []
    added_jokes = []
    for url, setup, punchline in one_liners:
        if not (used_urls['url'] == url).any():
            added_urls.append(url)
            added_jokes.append((setup, punchline))
    url_df = pd.DataFrame(added_urls, columns=['url'])
    jokes_df = pd.DataFrame(added_jokes, columns=['Joke', 'Punchline'])

    with open(url_file, 'a') as f:
        url_df.to_csv(f, index=False, header=False, encoding='utf-8')

    with open(joke_file, 'a') as f:
        jokes_df.to_csv(f, index=False, header=False, encoding='utf-8')

def ensure_existance(joke_file, url_file):
    if not os.path.isfile(url_file):
        with open(url_file, 'w') as f:
            f.write(u'url\n')

    if not os.path.isfile(joke_file):
        with open(joke_file, 'w') as f:
            f.write(u'Joke, Punchline\n')

def main():
    joke_file = sys.argv[1]
    url_file = sys.argv[2]
    ensure_existance(joke_file, url_file)
    urls = retrieve_urls()
    results = [retrieve_joke(url) for url in urls]
    one_liners = filter_results(urls, results)
    save_results(one_liners, joke_file, url_file)

if __name__ == '__main__':
    main()
