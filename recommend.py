#!/usr/bin/env python
#python guardian and Radio Times highlights parser from kbuss.co.uk
#to be used with TV Wish

from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
import datetime
import re
import urllib
import urllib2

################## UPDATE THESE FIELDS ####

filename = "recommendations.txt"
rt_commented = "true"  # change this value to true to comment out the radiotimes suggestions
g_commented = "true"   # change this value to true to comment out the guardian suggestions
minstars = 4  # set the minimum number of stars required for films
include_films = "true"
film_details = "true"  # fetch more detailed information about each film, this takes longer
#### Update the following fields to reflect your tastes and setup
unwanted_titles = [
                   'EastEnders',
                   'CSI: Miami',
                   'The Apprentice',
                   'Midsomer Murders',
                   ]
unwanted_channels = [
                     'Yesterday',
                     'Discovery Channel',
                     'PBS UK',
                     'Eden',
                     'Sky1',
                     'Sky2',
                     'Watch',
                     'Sky Living, HD',
                     'Sky Premiere',
                     'Sky Atlantic',
                     'Sky Arts 1',
                     'HD'
                     ]
## RADIO TIMES GENRES ##
# The full list of possible genres follows:
#genres = ['Drama,Soap', 'Entertainment,Reality,Food,Property,Lifestyle', 'Comedy,Sitcom', 'Arts,Music', 'Childrens', 'Sport', 'Documentary,Education,CurrentAffairs,News,History,Science,Nature']
# Delete unwanted lines below, each genre is fairly wide and includes the whole line, please remove the full line as it is part of the url, deleting part of the line will result in errors
genres = [
          'Drama,Soap',
          'Entertainment,Reality,Food,Property,Lifestyle',
          'Comedy,Sitcom',
          'Arts,Music',
          'Childrens',
          'Sport',
          'Documentary,Education,CurrentAffairs,News,History,Science,Nature'
          ]
########################################

date = str(datetime.date.today())
minstars = minstars - 1
day = datetime.date.isoweekday(datetime.date.today())


def getRadioTimesTV():
    output.append('\n############ TV from the Radio Times ############')
    for genre in genres:
        url = 'http://www.radiotimes.com/tv/recommendations?genre=' + genre
        print "Fetching TV programmes from the Radio Times for the genre " + genre
        try:
            doc = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            print 'HTTPError = ' + str(e.code)
        except urllib2.URLError as e:
            print 'URLError = ' + str(e.reason)
        except Exception:
            print 'generic exception: '
        soup = BeautifulSoup(doc)
        items = soup.findAll('article')
        i = 0
        length = len(items)
        length = length - 2  # This is because the last 2 article tags are not TV shows
        for item in items:
            title = None
            channel = None
            description = None
            if (0 < i < length):
                title = item.find('a').string.encode('ascii', 'ignore')
                channel = item.find('dd').string
                description = item.find('p').string
                if description is not None:
                    description = "\n#" + description.encode('ascii', 'ignore') + " " + channel
                else:
                    description = "\n# No description found " + channel
                if (not title.upper() in (name.upper() for name in unwanted_titles)) and (not channel in unwanted_channels):
                    if rt_commented == "true":
                        text = "\n#Show: " + title
                    else:
                        text = "\nShow: " + title
                    output.append(text)
                    output.append(description)
                unwanted_titles.append(title)
            i = i + 1


def getRadioTimesFilms():
    print "Fetching Film Information from the Radio Times"
    output.append('\n############ Films from the Radio Times ############')
    url = 'http://www.radiotimes.com/film/film-on-tv'
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib2.Request(url, None, headers)
        html = urllib2.urlopen(req).read()
        stripped = re.compile(r'<!.*?>')
        # get rid of the comments that upset beautiful soup
        html = stripped.sub('', html)
        soup = BeautifulSoup(html)
        lists = soup.find("div", {"id": "radiotimes"}).findNext('ul').findAll('li')
        for li in lists:
            title = None
            channel = None
            description = None
            stars = None
            titleUrl = li.find("a", {"class": "img-text-list-item-title"})
            if titleUrl is None:
                print "No Film information found"
                output.append("\nNo Film information found at " + url)
                return
            title = titleUrl.contents[0].encode('ascii', 'ignore')
            filmUrl = "http://www.radiotimes.com" + titleUrl['href']
            stars = li.span.contents[0]
            channel = li.time.contents[0]
            starrate = "\n#Stars:" + stars
            try:
                stars = int(stars)
            except:
                stars = 1
            if (stars > minstars):
                if (not title.upper() in (name.upper() for name in unwanted_titles)) and (not channel in unwanted_channels):
                    if film_details == "true":
                        print "Fetching more details for " + title
                        try:
                            doc = urllib2.urlopen(filmUrl)
                        except urllib2.HTTPError as e:
                            print 'HTTPError = ' + str(e.code)
                        except urllib2.URLError as e:
                            print 'URLError = ' + str(e.reason)
                        except Exception:
                            print 'generic exception: '
                        filmInfo = BeautifulSoup(doc)
                        reviewNode = filmInfo.find('p', {"itemprop": "reviewBody"})
                        if reviewNode is not None:
                            review = ''.join(reviewNode.findAll(text=True))
                        else:
                            review = ''
                        node = filmInfo.find('p', {"itemprop": "description"})
                        if node is not None:
                            description = ''.join(node.findAll(text=True))
                        else:
                            description = ''
                        director_year = filmInfo.find('li', {"class": "director_year"})
                        if director_year is not None:
                            director_year = director_year.contents[0]
                            year = director_year[director_year.find("("):director_year.find(")") + 1]
                            director = director_year[0:director_year.find("(")]
                        else:
                            year = ''
                            director = ''
                        certificate = filmInfo.find('li', {"id": "certificate"})
                        if certificate is not None:
                            certificate = certificate.contents[0]
                        else:
                            certificate = ''
                        description = "\n#Directed by " + director.encode('ascii', 'ignore') + " Rated: " + certificate.encode('ascii', 'ignore') + ". " + review.encode('ascii', 'ignore') + " " + description.encode('ascii', 'ignore') + " " + channel
                    else:
                        description = "\n#More information can be found at: " + filmUrl
                    if rt_commented == "true":
                        titleText = "\n#" + title + " " + year
                    else:
                        titleText = "\n" + title
                    output.append(titleText)
                    output.append(starrate)
                    output.append(description)
            unwanted_titles.append(title)
    except urllib2.HTTPError as e:
        print 'HTTPError = ' + str(e.code)
    except urllib2.URLError as e:
        print 'URLError = ' + str(e.reason)
    except Exception:
        print 'generic exception: '


def getGuardian():
    print "Fetching information from The Guardian"
    output.append('\n############ TV from the Guardian ############')
    url = "http://www.guardian.co.uk/culture/series/watchthis/rss"
    try:
        doc = minidom.parse(urllib.urlopen(url))
    except urllib2.HTTPError as err:
        print "An error occurred while opening the Guardian website:", err.reason
    body = doc.getElementsByTagName('description')[1].firstChild.nodeValue
    body = body.encode('UTF-8')
    soup = BeautifulSoup(body)
    shows = soup.findAll('h2')
    for show in shows:
        title = None
        channel = None
        description = None
        details = None
        title = show.find(text=True).encode('ascii', 'ignore')
        title = title.replace("&nbsp;", " ")
        detail = show.find('br').nextSibling
        details = detail.split(',')
        channel = details[1].strip()
        sib = show.findNext('p')
        # The following is to check for empty paragraphs
        while sib is not None and description is None:
            descriptions = sib.findAll(text=True)
            description = ''.join(descriptions)
            sib = sib.findNext('p')

        description = "\n#" + description.encode('ascii', 'ignore') + " " + detail
        description = description.replace("&nbsp;", " ")
        if (not title.upper() in (name.upper() for name in unwanted_titles)) and (not channel in unwanted_channels):
            if g_commented == "true":
                text = "\n#Show: " + title
            else:
                text = "\nShow: " + title
            output.append(text)
            output.append(description)
        unwanted_titles.append(title)

def main():

    #Fetch the data from the Guardian.
    #There is no new data on a Saturday or a Sunday.
    global output
    output = []
    if day < 6:
        getGuardian()

    getRadioTimesTV()

    if include_films == "true":
        getRadioTimesFilms()

    print "Writing to: " + filename
    record = open(filename, 'w')
    record.write("%s" % ("#TV highlights on "))
    record.write("%s" % (date))
    output = ''.join(output)
    record.write(output)
    print "All done, closing the file"
    record.close()


if __name__ == "__main__":
    main()
