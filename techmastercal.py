from bs4 import BeautifulSoup
import urllib
import re
from icalendar import Calendar, Event
from datetime import datetime
import pytz

eventtitles = []
ongoingtitles= []
starttime = {}
startongoing = {}
endtime = {}
endongoing = {}
location = {}
locationongoing = {}
seminarname = {}
seminarongoing = {}

url = urllib.urlopen('https://www.caltech.edu/master-calendar/day').read()
soup = BeautifulSoup(url, 'html.parser')

i = 0
j = 0
k = 0
m = 0

for table in soup.findAll('table', {'class' : 'events day'}):
    for a in table.findAll('a', {'href': \
                 re.compile('^(/content/.*)')}):                 
        eventtitles.append(' '.join(a.contents))

    for start in table.findAll('div', 'start_date'):
        starttime[eventtitles[i]] = start.contents[0]
        i += 1

    for end in table.findAll('div', 'end_date'):
        endtime[eventtitles[j]] = end.contents[0]
        j += 1

    for td in table.findAll('td', 'event-info'):
        a = td.find('div')
        output = a['class'][0]
        found = False
        parent = a.find_parent('td')
        
        while not found: 
            if output == 'event-location':
                location[eventtitles[k]] = a.contents[0]
                found = True
            else:
                a = a.find_next('div')
                output = a['class'][0]
                newparent = a.find_parent('td')
                if newparent != parent:
                    break
        k += 1

        a = td.find('div')
        output = a['class'][0]
        found = False
        parent = a.find_parent('td')
        found = False

        while not found:
            if output == 'seminar-title':
                seminarname[eventtitles[m]] = a.contents[0]
                found = True
            else:
                a = a.find_next('div')
                output = a['class'][0]
                newparent = a.find_parent('td')
                if newparent != parent:
                    break

        m += 1

i = 0
j = 0
k = 0
m = 0

for table in soup.findAll('table', 'events day ongoing'):
    for a in table.findAll('a', {'href': re.compile(\
                            '^(/content/.*)')}):
        ongoingtitles.append(' '.join(a.contents))

    for start in table.findAll('div','start_date'):
        startongoing[ongoingtitles[i]] = start.contents[0]
        i += 1

    for end in table.findAll('div', 'end_date'):
        endongoing[ongoingtitles[j]] = end.contents[0]
        j += 1


    for td in table.findAll('td', 'event-info'):
        a = td.find('div')
        output = a['class'][0]
        found = False
        parent = a.find_parent('td')
        
        while not found: 
            if output == 'event-location':
                locationongoing[ongoingtitles[k]] = a.contents[0]
                found = True
            else:
                a = a.find_next('div')
                output = a['class'][0]
                newparent = a.find_parent('td')
                if newparent != parent:
                    break
        k += 1

        a = td.find('div')
        output = a['class'][0]
        found = False
        parent = a.find_parent('td')
        found = False

        while not found:
            if output == 'seminar-title':
                seminarongoing[ongoingtitles[m]] = a.contents[0]
                found = True
            else:
                a = a.find_next('div')
                output = a['class'][0]
                newparent = a.find_parent('td')
                if newparent != parent:
                    break

        m += 1

i = 1

for event in eventtitles:
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    pacific = pytz.timezone('America/Los_Angeles')
    calevent = Event()
    calevent.add('summary', event)
  
    if seminarname.get(event) == None:
    	pass
    else: 
        calevent.add('description', seminarname.get(event))

    now = datetime.now()

    eventstart = starttime[event]
    eventend = endtime[event]
    startsplit = eventstart.split()
    endsplit = eventend.split()
    
    starthour = startsplit[0].split(':')[0]
    startminute = startsplit[0].split(':')[1]
    endhour = endsplit[0].split(':')[0]
    endminute = endsplit[0].split(':')[1]

    if startsplit[1] == 'pm': 
    	starthour = int(starthour) + 12
    if endsplit[1] == 'pm':
        endhour = int(endhour) + 12
    
    calevent.add('dtstart', datetime(now.year, now.month, now.day, \
            int(starthour), int(startminute), 0, tzinfo = pacific))
    calevent.add('dtend', datetime(now.year, now.month, now.day, \
            int(endhour), int(endminute), 0, tzinfo = pacific))
    
    if location.get(event) == None:
        pass
    else:
        calevent.add('location', location.get(event))

    cal.add_component(calevent)
    f = open('test' + str(i) + '.ics', 'w')
    f.write(cal.to_ical())
    f.close()
    
    i += 1
