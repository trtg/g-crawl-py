import qless
import gcrawl
import pyreBloom
import title_crawler

#Usage:
#Before you run this script, start up some worker processes like this:
#qless-py-worker --path /path/to/where_this_script_is/  -q crawl --verbose --interval 5
#NOTE: you must specify that path otherwise you will get "No such module" errors when the
#job actually runs

client = qless.client()
queue = client.queues['crawl']

#how should the max_pages limit be set?, if you just keep going till there's no more
#links to follow, you might never stop on sites which frequently add user
#contributed content
queue.put(title_crawler.TitleCrawler,{'seed':'http://www.webmd.com','max_pages':3})
