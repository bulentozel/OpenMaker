# -*- coding: utf-8 -*-
import scrapy, re, csv
import sys
import os.path


class WikipediaSpider(scrapy.Spider):
    name = "wikipedia"
    depth = 1
    document_id = 1
    SiteStopWords = [
        'navigation',
        'search',
        'References',
        'History',
        'Contents',
        'edit'
        ]
    SiteStopPhrases = [
        'From Wikipedia the free encyclopedia',
        'See also',
        'External links',
        'Jump to',
        'Main article'
        ]
    def read_root_urls(self, urlfile):
        """It reads list of urls from comma sperated textfile.


        Args:
            urlfile (str): the name of external file.
            
            Note that each row should have a theme identifier, depth, theme name and url.
            Format:
            0, 1, diy, https://en.wikipedia.org/wiki/Do_it_yourself,
            0, 1, diy, https://en.wikipedia.org/wiki/Open_design,
            1, 2, sustainability, https://en.wikipedia.org/wiki/sustainability

        Returns:
            A python list of tuples with theme Id and the url.
        """

        with open(urlfile) as csvfile:
            urls = list()
            urlreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(urlreader, None)
            for row in urlreader:
                themeid = int(row[0].strip())
                max_depth = int(row[1].strip())
                theme = row[2].strip()
                url = row[3].strip()
                newroot = (themeid,max_depth,theme,url)
                urls.append(newroot)
            return urls
                
    def start_requests(self):
        """
        Example input format:
        [theme_id, depth_of_crawling, category_name, seed_url]
        urls = [
            0, 1, DIY, 'https://en.wikipedia.org/wiki/Do_it_yourself'
        ]
        """
        infile = getattr(self, 'infile', None)
        if infile is None:
            message = 'An input file with seed url is needed!\n Example run:\n scrapy crawl wikipedia -o test.json -a infile="./input_urls.txt"'
            print(message)
            raise scrapy.exceptions.CloseSpider(reason='cancelled')
            
        urls = self.read_root_urls(infile)
        
        for entry in urls:
            url = entry[3]
            print(url)
            themeid = entry[0]
            theme = entry[2]
            max_depth = entry[1]
            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['depth'] = 0
            request.meta['theme'] = theme
            request.meta['theme_id'] = themeid
            request.meta['max_depth'] = max_depth
            yield request
            
    def parse(self, response):
        depth = response.meta['depth']
        theme = response.meta['theme']
        themeid = response.meta['theme_id']
        max_depth = response.meta['max_depth']
        url = response.url
        title = response.xpath('//title/text()').re('(.*) - (.*)')[0]
        text = self._render_text(response)
        docid = self.document_id
        self.document_id += 1
        yield {
            'theme': theme,
            'theme.id': themeid,
            'document.id': docid,
            'title': title,
            'url': response.url,
            'depth': depth,
            'text': text
            }

        depth += 1
        if depth > max_depth: return

        links = self._extract_links(response)
        for link in links:
            if not  link: continue
            next_page = response.urljoin(link)
            request = scrapy.Request(next_page, callback=self.parse)
            request.meta['depth'] = depth
            request.meta['theme'] = theme
            request.meta['theme_id'] = themeid
            request.meta['max_depth'] = max_depth
            yield request
            
    def _extract_links(self, response):
        """ This part aims to extract wiki links within after the section called 'See also and
            before the section called References.

        TO DO:
            - Needs to be revised via more tests.
        """
        before_References = response.xpath('//h2/span[@id="References"]/preceding::ul/li/a[@title | @href]/@href').re('/wiki/.*')
        after_See_also = response.xpath('//h2/span[@id="See_also"]/following::ul/li/a[@title | @href]/@href').re('/wiki/.*')

        see_also = list(set(before_References).intersection(set(after_See_also)))
        if see_also:
            return see_also
        else:
            after_References = response.xpath('//h2/span[@id="References"]/following::ul/li/a[@title | @href]/@href').re('/wiki/.*')
            before_See_also = response.xpath('//h2/span[@id="See_also"]/preceding::ul/li/a[@title | @href]/@href').re('/wiki/.*')
            return list(set(after_References).intersection(set(before_See_also)))
        

    def _render_text(self, response):
        """ It extracts the main body of the article as well as text used under images, tables, etc. and cleans the text.
            The text until the Reference section of the article is considered.

        TO DO:
            - There are automaticaly generated content for the Wikipedia articles, such as,
                - Concepts
                - Organizations
                - People, etc.
            Such content is held usually out of the main body of the article. These fields should be considered for the rendering.

        """
        main = [text for text in response.xpath('//h2/span[@id = "References"]/preceding::text()').extract() if text.strip()]
        head = [text for text in response.xpath('//body/preceding::text()').extract() if text.strip()]

        # Removing header part:
        body0 = main[len(head):]

        # Remove unicode characters:
        body1 = [re.sub(r'[^\x00-\x7F]+','', t) for t in body0]

        # Remove URLs
        body2 = [t.split() for t in body1]
        body2 = [[x for x in y if not "://" in x] for y in body2]
        body2 = [y for y in body2 if y]
        body2 = [" ".join(y) for y in body2]

        # Romove "[]_()\,:.;":
        body2 = [re.sub(r'[\[\]\(\)\\.,;:_]+',' ', t) for t in body2]

        # Remove number only literals:
        body3 = [t.split() for t in body2]
        body3 = [y for y in body3 if y]
        body3 = [[x for x in y if not x.isdigit()] for y in body3]
        body3 = [y for y in body3 if y]

        ## Remove Wikipedia specific stop words and phrases:
        body4 = [" ".join(y) for y in body3 if not (len(y)==1 and y[0] in self.SiteStopWords)]
        
        SplitSSP = [x.split() for x in self.SiteStopPhrases]
        body5 = [x for x in body4 if x.split() not in SplitSSP]
        body = " \n ".join(body5)
        return body
