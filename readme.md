General mechanism:

* First time you request the index page, web scraping of 10 most recent articles (https://www.aljazeera.com/news/) will start. Package used for web scraping is beautiful soup. 
* When an article is fetched, it starts sentiment analysis. It does following steps: 
  * Do sentence subjectivity and polarity analysis via text blob and plot histogram based on each sentence of the article. I used the ploty JS lib.
  * Do vocabulary frequency analysis since this can give a direct impression of article topic:
    * words cleaning: clean any non-essential words such as stop words and non-alpha.
    * plot top 25 most common words frequency graph.
    * generate word cloud img (Put img files in media folder on server)


![Alt Text](demo.gif)
