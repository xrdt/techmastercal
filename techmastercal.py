from bs4 import BeautifulSoup
import urllib
from icalendar import Calendar, Event
from datetime import datetime
import time
import pytz
import re

url = urllib.urlopen('https://www.caltech.edu/master-calendar/day').read()
soup = BeautifulSoup(url, 'lxml')

def get_eventnames():
    '''pulls all the event names from the website and stores them in a list
       so we can add them all to the calendar using icalendar'''
    eventnames = []
    for event in soup.findAll('div', 'event-title'):
        a_tag = event.find('a')
        event_name = a_tag.string
        if event_name is None:
            [x.replaceWithChildren() for x in a_tag.findAll('em')]
            if len(a_tag.contents) > 1:
                a_tag = ''.join(a_tag)
            event_name = a_tag
        eventnames.append(event_name)
    return eventnames

def get_starttimes(eventnames):
    '''pulls all start times from the website and stores them in a 
       dictionary {eventname:starttime}.'''
    starttimes = {}
    i = 0
    for start in soup.findAll('div', 'start_date'):
        len_start = len(start.string)
        start_time = start.string[:len_start-3]  
        event_title = start.findNext('div', 'event-title')
        eventname = event_title.string
        if eventname is None:
            eventname = eventnames[i]
        starttimes[eventname] = start_time
        i += 1
    return starttimes

def get_endtimes(eventnames):
    '''pulls all start times from the website and stores them in a 
       dictionary'''
    endtimes = {}
    i = 0
    for end in soup.findAll('div', 'end_date'):
        end_time = end.string
        event_title = end.findNext('div', 'event-title')
        eventname = event_title.string
        if eventname is None:
            eventname = eventnames[i]
        endtimes[eventname] = end_time
        i += 1
    return endtimes

def get_locations():
    '''pulls all event locations from the website and stores them in 
       a dictionary. not every event has a location, so using a 
       dictionary is a way to see which events have a location'''
    locations = {}
    for div_location in soup.findAll('div', 'event-location'):
        location = div_location.string
        event_title = div_location.findPreviousSibling('div', 'event-title')
        eventname = event_title.string
        locations[eventname] = location
    return locations

def get_seminarnames():
    '''pulls all seminar names from the website and stores them in 
       a dictionary, same deal as get_locations'''
    seminarnames = {}
    for seminar_title in soup.findAll('div', 'seminar-title'):
        seminarname = seminar_title.string
        event_title = seminar_title.findPreviousSibling('div', \
                'event-title')
        eventname = event_title.string
        seminarnames[eventname] = seminarname
    return seminarnames

def get_speakers():
    '''pulls all speaker names and stores them in dictionary with keys as
       events and values as speaker names and descriptions.'''
    speakernames = {} 
    p = re.compile('^field field-name-speaker[a-zA-Z- ]*')
    for speaker_div in soup.findAll('div', re.compile(p)):
        level1 = speaker_div.contents[0]
        level2 = level1.contents[0]
        level3 = level2.contents[0]
        name = level3.contents[0]
        speaker = name.string
        parent1 = speaker_div.parent
        parent2 = parent1.parent
        parent3 = parent2.parent
        event_title = parent3.findPreviousSibling('div', 'event-title')
        eventname = event_title.string
        speakernames[eventname] = speaker
    return speakernames

def create_description(seminarnames, speakers):
    descriptions = {}
    for event in seminarnames:
        if speakers.get(event) == None:
            descriptions[event] = seminarnames.get(event)
        else:
            combined = seminarnames.get(event) + '\n' + speakers.get(event)
            descriptions[event] = combined
    return descriptions

def main_events():
    eventnames = get_eventnames()
    starttimes = get_starttimes(eventnames)
    endtimes = get_endtimes(eventnames)
    seminarnames = get_seminarnames()
    locations = get_locations()
    speakernames = get_speakers()
    descriptions = create_description(seminarnames, speakernames)
    return eventnames, starttimes, endtimes, locations, descriptions
           
class cal_events():
    now = datetime.now()
    pacific = pytz.timezone('America/Los_Angeles')
            
    def add_times(self, eventstart, eventend):
        starthour = startminute = endhour = endminute = startmonth = \
                startday = endmonth = endday = None
        if len(eventstart) > 5:
            startsplit = eventstart.split()
            starthour = startsplit[0].split(':')[0]
            startminute = startsplit[0].split(':')[1]
            if startsplit[1] == 'pm' and int(starthour) < 12: 
                starthour = int(starthour) + 12
        else:            
            startmonth = eventstart.split('/')[0]
            startday = eventstart.split('/')[1]

        if len(eventend) > 5:
            endsplit = eventend.split()
            endhour = endsplit[0].split(':')[0]
            endminute = endsplit[0].split(':')[1]
            if endsplit[1] == 'pm' and int(endhour) < 12:
                endhour = int(endhour) + 12
        else:
            endmonth = eventend.split('/')[0]
            endday = eventend.split('/')[1]

        if startmonth:
            if endmonth:
                pass
            else:
                today = time.strftime('%d/%m/%y')
                endmonth = today.split('/')[1]
                endday = int(today.split('/')[0]) + 1
                endhour = None
                starthour = None

        return_tuple = ()
        if starthour:
            return_tuple += (starthour, startminute)
        if endhour:
            return_tuple += (endhour, endminute)
        if startmonth:
            return_tuple += (startmonth, startday)
        if endmonth:
            return_tuple += (endmonth, endday)
        return return_tuple 
        	
    def add_events(self, eventnames, locations, starttimes, \
            endtimes, descriptions):
        i = 1
        for event in eventnames:
            cal = Calendar()
            cal.add('prodid', '-//My calendar product//mxm.dk//')
            cal.add('version', '2.0')

            calevent = Event()
            calevent.add('summary', event)

            if descriptions.get(event) == None:
                pass
            else: 
                calevent.add('description', descriptions.get(event))

            if locations.get(event) == None: 
                pass
            else: 
                calevent.add('location', locations.get(event))
            
            if starttimes.get(event) == None:
                calevent.add('dtstart', datetime(self.now.year, \
                        self.now.month, self.now.day, 0, 0, 0, \
                        tzinfo = self.pacific))
                calevent.add('dtend', datetime(self.now.year, \
                        self.now.month, self.now.day + 1, 0, 0, 0, \
                        tzinfo = self.pacific))

            elif len(starttimes[event]) > 5:
                starthour, startminute, endhour, endminute = \
                    self.add_times(starttimes[event], endtimes[event])

                calevent.add('dtstart', datetime(self.now.year, \
                self.now.month, self.now.day, int(starthour), \
                int(startminute), 0, tzinfo = self.pacific))

            elif len(starttimes[event]) <= 5:
                startmonth, startday, endmonth, endday = \
                        self.add_times(starttimes[event], endtimes[event])
                calevent.add('dtstart', datetime(self.now.year, \
                        int(startmonth), int(startday), \
                        tzinfo = self.pacific))
            
            if endtimes.get(event) == None:
                pass
            elif len(endtimes[event]) > 5:
                starthour, startminute, endhour, endminute = \
                        self.add_times(starttimes[event], endtimes[event])
                calevent.add('dtend', datetime(self.now.year, \
                self.now.month, self.now.day, int(endhour), \
                int(endminute), 0, tzinfo = self.pacific))

            elif len(endtimes[event]) <= 5:
                startmonth, startday, endmonth, endday = \
                        self.add_times(starttimes[event], endtimes[event])
                calevent.add('dtend', datetime(self.now.year, \
                        int(endmonth), int(endday), tzinfo = self.pacific))

            cal.add_component(calevent)
            f = open('event' + str(i) + '.ics', 'w')
            f.write(cal.to_ical())
            f.close()
            i += 1

if __name__ == '__main__':
    eventnames, starttimes, endtimes, locations, descriptions \
            = main_events()
    calendar = cal_events()
    calendar.add_events(eventnames, locations, starttimes, \
            endtimes, descriptions)
