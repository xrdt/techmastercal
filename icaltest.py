from icalendar import Calendar, Event
from datetime import datetime
import pytz

pacific = pytz.timezone('America/Los_Angeles')

cal = Calendar()
event = Event()
event.add('summary', 'Hello')
event.add('description', 'yesyesyes')
event.add('dtstart', datetime(2016, 9, 27, 12, 0, 0, tzinfo = pacific))
event.add('dtend', datetime(2016, 9, 27, 13, 0, 0, tzinfo = pacific))
event.add('location', 'yaya boo')

cal.add_component(event)
f = open('test.ics', 'w')
f.write(cal.to_ical())
f.close()
