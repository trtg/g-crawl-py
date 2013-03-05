#this is just a standalone test of subclassing the crawler and running it WITHOUT qless
import gcrawl
import pyreBloom
import redis

red = redis.Redis()

#instantiate the class with a seed URL like http://www.livestrong.com
#
#internally, self.crawl() calls self.run() which starts up the main loop.
#this then calls self.got() which adds all the followable links in the page you fetched to self.requests
#or if the page you got returned a redirect (301,302,303,307) add that to self.requests. The run loop keeps
#going while self.requests is not empty and just repeatedly calls self.pop() and retrieves that URL

class TitleCrawler(gcrawl.Crawl):
        
    def __init__(self,*args,**kwargs):
        super(TitleCrawler,self).__init__(*args,**kwargs)
        self.bloomfilt= pyreBloom.pyreBloom('titles_bloomfilter',100000,0.01)

    def delay(self, page):
        """Return how many seconds to wait before sending the next request in this crawl"""
        return 5
    
    def count(self, page):
        """ Should this page count against the max_pages count"""
        #we don't count redirects against our total/max pages to crawl
        return page.status not in (301,302,303,307)

    def got(self,page):
        '''We fetched a page. Here is where you should decide what
        to do. For now we add all the links on the page to the queue 
        of links to be crawled and store the body of the page in s3 
        to be analyzed later if it hasn't already been crawled'''
        print "GOT ",page.url," with status ",page.status
        if page.status in (301, 302, 303, 307):
            self.extend([page.redirection], page)
        else:
            if page.url not in self.bloomfilt:
                self.bloomfilt.extend(page.url)
                self.extend(page.links['follow'], page)
                print "writing ",page.url," to redis"
                red.hset('page_bodies',page.url,page.content)
            else:
                print "already crawled ",page.url

        return None

myCrawler = TitleCrawler("http://www.webmd.com",max_pages=3)
myCrawler.run()
