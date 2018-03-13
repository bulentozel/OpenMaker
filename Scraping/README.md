# Wikipedia Crawler
This is a Wikipedia scraper which scrapes semanticly related articles up to a predermined depth.

In order to run the scraper:
1. Install Scrapy: https://doc.scrapy.org/en/latest/intro/install.html
2. Go to the folder where you can run the crawler:
```
cd ./GitHub/OpenMaker/Scraping/wikipedia
```
3. Run the following command: 
```
scrapy crawl wikipedia -o ../../Semantics/data/corpuses/achievement.json -a infile="./achievement_urls.txt" 
```
* Note that the part after -o is the outputfile
* Note that the part after -a infile= is the file where list of root urls are to be provided.
## Important Notes:
* Every time you run the crawler it will incrementally add new entries to the output file. So either use a different file name or remove the current file "wikipedi.json" if needed.

