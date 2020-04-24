# rss

a simple python script that aggregates rss and atom feeds and generates static HTML pages or plain text from them.

it grabs the previous 90 days' stories from the feed(s) and turns them into a simple HTML list, that looks like this:

intended to be run on a schedule, perhaps as a cron job.

## usage

    usage: rss.py [-h] [--out-html OUT_HTML] [--out-plain OUT_PLAIN]
                  [--title TITLE] [--hide-feed-names] [--include-content]
                  input

    positional arguments:
      input                 the URL of a feed or a file containing a newline
                            separated list of feeds

    optional arguments:
      -h, --help            show this help message and exit
      --out-html OUT_HTML   a file to write html output to
      --out-plain OUT_PLAIN
                            a file to write plain text output to
      --title TITLE         a title for the generated page
      --hide-feed-names     hide the names of feeds in the output
      --include-content     include the content of the feed items

## examples

basic usage, take a single feed output HTML to stdout

    $ python rss.py http://feeds.bbci.co.uk/news/science_and_environment/rss.xml 

basic usage with multiple feeds

    $ cat feeds
    http://feeds.bbci.co.uk/news/science_and_environment/rss.xml
    http://feeds.bbci.co.uk/news/technology/rss.xml
    $ python rss.py feeds

output both HTML and plain text

    $ python rss.py http://feeds.bbci.co.uk/news/science_and_environment/rss.xml --out-html bbc.html --out-plain bbc.txt

## customisation

the templates for both the HTML and plain text output are at the top of rss.py. these are jinja2 templates and are easy to modify
