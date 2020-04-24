import time
import sys
from datetime import datetime, timedelta
from itertools import cycle
import argparse
import re
import textwrap
from pprint import pprint
from jinja2 import Template

import feedparser

colours = ['#005784', '#A3CE27', '#EB8931', '#BE2633', '#31A2F2', '#9D9D9D']

# variables passed to these templates:
#   args..........command line arguments
#   title.........feed title
#   colours.......list above
#   items.........list of feed items, each items contains:
#     link........URL to the item
#     date........published date of the item
#     feed_title..title of the feed the item is from
#     content.....content of the item
#     colour......index of the colour to use in the colours array

htmlTemplate = Template('''
<!doctype HTML>
<html>
    <head>
        <meta name="viewport" content="width=device-width">
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <link href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABwUlEQVR4nO2aMW7DMAxF1SKX8hEyevSSvSfqnsWjxx7Bx0omBUahSCSlT9IIH5Atkc1nipQcpRQEQRAEwafyxfny9f7z6LnY3+2XdT0NSDfUG3gJLzLMBByxlNG8MDr4IxYi2AKWeSINvG678JZ0RcAElOBI0ZKgKiDjScQ3cvB3LPP0+rRA1yATAUcoIpASzAVkKBIQItwISMkmG1wJyGhKcCkgJT0JF+4PqC1sRLtc5qlrQUVBZSncK6MmoXedoL4XkMpASVCvAeu2i9K6Jq7nIZkVwdESpJh2AUk2vJMgzQIXbdBSArsNUtJQkt7rtkNSvAUkAzi7vSMccaOyAD4FuCJGSOCgVgNQEkpwskC1CEqmBWXMHszeCLVA7wEyZm0QLYE6DUzXAaOmQ884LhZCNU63HZY8jVaQPX/GtHaKwzNg5PpeA9gUGJm6yGkArQHaqzoJ8CKo1c+lqHSBERIoY0iyyFUbtJgG7PcBmf8323pCVvv9FqIMKAXiMTgKbAG1QM8owVUNsCAEWN+ANWwBtWrvfdFTQpQBpUDPGHxKzg5KImhth10clUVB+df444ug6nF5LbycRA+CIAiCwDdPu5XNGOUoGnAAAAAASUVORK5CYII=" rel="icon" type="image/x-icon" />
        <style>
        body {
            max-width: 86ex;
            margin: 0 auto;
            padding: 0 1rem 1rem 1rem;
            font-family: system, -apple-system, ".SFNSText-Regular", "San Francisco", "Roboto", "Segoe UI", "Helvetica Neue", "Lucida Grande", sans-serif;
        }

        body.dark-theme {
          color: #eee;
          background-color: #333;
        }
        .dark-theme a {
          color: #ddd;
        }
        .dark-theme a:visited {
          color: #ddd;
        }
        .dark-theme footer {
          color: rgba(255, 255, 255, 0.5);
        }

        .feed-item {
            margin-bottom: 1rem;
            padding-left: 1ex;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .feed-item__feed {
            font-size: 10pt;
            color: #aaa;
        }
        .feed-content {
            line-height: 1.5;
            margin-bottom: 1rem;
        }
        footer {
            font-size: 10pt;
            color: rgba(0, 0, 0, 0.5);
        }
        h2 {
          margin: 0;
        }
        img {
            max-width: 100%;
        }
        .header {
          display: flex;
          justify-content: space-between;
          margin: 2rem 0;
        }
        {% for colour in colours %}
            .colour-{{ loop.index0 }} {
                border-left: 3px solid {{ colour }};
            }
        {% endfor %}
        </style>
    </head>
    <body class="dark-theme">
        <div class="header">
            <h2>{{ title }}</h2>
        </div>
        {% for item in items %}
            {% if args.include_content %}
                <details>
                    <summary class="feed-item colour-{{ item.colour }}">
                        <a href="{{ item.link }}">{{ item.date}} - {{ item.title }}</a>
                        {% if not args.hide_feed_names %}
                             <div class="feed-item__feed">{{ item.feed_title }}</div>
                        {% endif %}
                    </summary>
                    <div class="feed-content">{{ item.content }}</div>
                </details>
            {% else %}
                <div class="feed-item colour-{{ item.colour }}">
                    <a href="{{ item.link }}">{{ item.date}} - {{ item.title }}</a>
                    {% if not args.hide_feed_names %}
                         <div class="feed-item__feed">{{ item.feed_title }}</div>
                    {% endif %}
                </div>
            {% endif %}
        {% endfor %}
    <footer>generated on {{ date }}</footer>
    </body>
</html>
''', trim_blocks=True, lstrip_blocks=True)

rawTemplate = Template('''\
{% for item in items %}\
{{ item.date }} - {{ item.title }}{%if not args.hide_feed_names %} - {{ item.feed_title }}{% endif %}
  {{ item.link }}\n
{% endfor %}
''')

def genHtml(args, items):
    return htmlTemplate.render(
        args=args,
        colours=colours,
        title=args.title if args.title is not None else 'feeds',
        items=items,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )

def genRaw(args, items):
    return rawTemplate.render(
        args=args,
        colours=colours,
        title=args.title if args.title is not None else 'feeds',
        items=items,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='the URL of a feed or a file containing a newline separated list of feeds')
    parser.add_argument('--out-html', type=argparse.FileType('w'),
                        help='a file to write html output to')
    parser.add_argument('--out-plain', type=argparse.FileType('w'),
                        help='a file to write plain text output to')
    parser.add_argument('--title',
                        help='a title for the generate page')
    parser.add_argument('--hide-feed-names', action='store_true',
                        help='hide the names of feeds in the output')
    parser.add_argument('--include-content', action='store_true',
                        help='include the content of the feed items')

    args = parser.parse_args()

    feeds = []
    if args.input.startswith('http://') or args.input.startswith('https://'):
        feeds = [args.input.strip()]
    else:
        try:
            feeds = open(args.input, 'r').readlines()
        except FileNotFoundError as e:
            sys.stderr.write(f'couldn\'t open file \'{args.input}\': {e}\n')
            sys.exit(1)
        feeds = map(lambda x: x.strip(), feeds)

    # get 90 days ago, as a unix timestamp
    start = time.mktime((datetime.utcnow() - timedelta(days=90)).timetuple())

    colours_cycle = cycle(range(len(colours)))

    items = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        if feed.status not in [200, 301, 302]:
            sys.stderr.write('fetching feed {} errored with status code {}\n'.format(feed_url, feed.status))
            continue
        feed_title = feed.feed.title
        colour = next(colours_cycle)
        for item in feed.entries:
            date = None
            if 'published_parsed' in item:
                date = item['published_parsed']
            elif 'date_parsed' in item:
                date = item['date_parsed']

            # ignore old posts
            if date is None or time.mktime(date) < start:
                continue

            title = item['title']
            link = item['link']
            date = time.strftime('%Y-%m-%d', date)
            items.append({
                'feed_title': feed_title,
                'title': title,
                'link': link,
                'date': date,
                'content': item['content'][0].value if 'content' in item else item['description'],
                'colour': colour,
            })

    items = sorted(items, key=lambda x: x['date'], reverse=True)

    writtenFile = False
    if args.out_html is not None:
        args.out_html.write(genHtml(args, items))
        args.out_html.close()
        writtenFile = True

    if args.out_plain is not None:
        args.out_plain.write(genRaw(args, items))
        args.out_plain.close()
        writtenFile = True

    # if we didn't write any files, write html to stdout
    if not writtenFile:
        sys.stdout.write(genHtml(args, items))
