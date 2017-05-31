__Another episode in the series of "repurposing" a public API!__

# Introduction
I needed "some" text data to train [MITIE](https://github.com/mit-nlp/MITIE) and create a proper word feature extractor for the Dutch language. I figured I would use some form of modern Dutch to get started, and [NU.nl](https://www.nu.nl/) seemed like an excellent first target. Opening up the Chrome console like a true hacker, it took me all of 3 minutes to find their (apparently not rate-limited) API. Hence, a quick and dirty script.

# How it works
Honestly, just read the source, it's pretty straightforward. Generally:  
* Requests all the article URIs from the API with some sleeper interval between so as not to completely hammer their API
* Stores them in a text file
* Once it reaches the end, it starts looping through the links text file and downloads all the articles
* Slams the extracted text in a text file

# You should've used a database
I know, I know, I don't know what I was thinking, but remember I said 'quick and dirty'? 