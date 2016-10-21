from bs4 import BeautifulSoup
import urllib
from icalendar import Calendar, Event
from datetime import datetime
import pytz

url = urllib.urlopen('https://www.caltech.edu/master-calendar/day').read()
soup = BeautifulSoup(url, 'lxml')

def get_eventnames():
    '''pulls all the event names from the website and stores them in a list
       so we can add them all to the calendar using icalendar'''
    eventnames = []
    for event in soup.findAll('div', 'event-title'):
        a_tag = event.find('a')
        event_name = a_tag.string
        eventnames.append(event_name)
    return eventnames

def get_starttimes():
    '''pulls all start times from the website and stores them in a 
       dictionary {eventname:starttime}.'''
    starttimes = {}
    i = 0
    for start in soup.findAll('div', 'start_date'):
        len_start = len(start.string)
        start_time = start.string[:len_start-3]  
        event_title = start.findNext('div', 'event-title')
        eventname = event_title.string
        starttimes[eventname] = start_time
        i += 1
    return starttimes

def get_endtimes():
    '''pulls all start times from the website and stores them in a 
       dictionary'''
    endtimes = {}
    i = 0
    for end in soup.findAll('div', 'end_date'):
        end_time = end.string
        event_title = end.findNext('div', 'event-title')
        eventname = event_title.string
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

def main_events():
    eventnames = get_eventnames()
    starttimes = get_starttimes()
    endtimes = get_endtimes()
    seminarnames = get_seminarnames()
    locations = get_locations()
    return eventnames, starttimes, endtimes, seminarnames, locations


class cal_events():
    now = datetime.now()
    pacific = pytz.timezone('America/Los_Angeles')
            
    def add_times(self, eventstart, eventend):
        if len(eventstart) > 5:
            startsplit = eventstart.split()
            endsplit = eventend.split()
            starthour = startsplit[0].split(':')[0]
            startminute = startsplit[0].split(':')[1]
            endhour = endsplit[0].split(':')[0]
            endminute = endsplit[0].split(':')[1]

            if startsplit[1] == 'pm' and int(starthour) < 12: 
                starthour = int(starthour) + 12
            if endsplit[1] == 'pm' and int(endhour) < 12:
                endhour = int(endhour) + 12
            return starthour, startminute, endhour, endminute

        else: 
            startmonth = eventstart.split('/')[0]
            startday = eventstart.split('/')[1]
            endmonth = eventend.split('/')[0]
            endday = eventend.split('/')[1]
            return startmonth, startday, endmonth, endday 
        	
    def add_events(self, eventnames, seminarnames, locations, starttimes, \
            endtimes):
        i = 1
        for event in eventnames:
            cal = Calendar()
            cal.add('prodid', '-//My calendar product//mxm.dk//')
            cal.add('version', '2.0')

            calevent = Event()
            calevent.add('summary', event)

            if seminarnames.get(event) == None:
                pass
            else: 
                calevent.add('description', seminarnames.get(event))

            if locations.get(event) == None: 
                pass
            else: 
                calevent.add('location', locations.get(event))
            
            if len(starttimes[event]) > 5:
                starthour, startminute, endhour, endminute = \
                    self.add_times(starttimes[event], endtimes[event])

                calevent.add('dtstart', datetime(self.now.year, \
                self.now.month, self.now.day, int(starthour), \
                int(startminute), 0, tzinfo = self.pacific))

                calevent.add('dtend', datetime(self.now.year, \
                self.now.month, self.now.day, int(endhour), \
                int(endminute), 0, tzinfo = self.pacific))
            else: 
                startmonth, startday, endmonth, endday = \
                        self.add_times(starttimes[event], endtimes[event])
                calevent.add('dtstart', datetime(self.now.year, \
                        int(startmonth), int(startday), \
                        tzinfo = self.pacific))
                calevent.add('dtend', datetime(self.now.year, \
                        int(endmonth), int(endday), tzinfo = self.pacific))

            cal.add_component(calevent)
            f = open('event' + str(i) + '.ics', 'w')
            f.write(cal.to_ical())
            f.close()
            i += 1

if __name__ == '__main__':
    eventnames, starttimes, endtimes, seminarnames, locations \
            = main_events()
    calendar = cal_events()
    calendar.add_events(eventnames, seminarnames, locations, starttimes, \
            endtimes)
