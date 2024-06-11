import json
import datetime
import requests
import re
import os

images_root = 'https://computingthehumanexperience.com/wp-content/themes/valeriya-child/timeline/attachments/'

# data
data = json.load(open('data/timeline.json'))
raw_events = data['eventUpdates']
events = []

titles_map = {}
places_map = {}
places = []

def add_place(item):
    if item['summary'].get('Place'):
        place = item['summary'].get('Place')
        if place and not places_map.get(place):
            places_map[place] = True
            places.append(place)


def summaryObject(summary):
    lines = summary.splitlines()
    object = {}

    object['Summary'] = summary

    for line in lines:
        key = 'Description'

        if ':' in line:
            key = re.sub('[:].*', '', line).strip()

        object[key] = re.sub('.*?[:]', '', line).strip()

    return object


for raw_event in raw_events:
    date_string = raw_event['dateString']
    is_bc = date_string.endswith(' BC')
    title = raw_event['title']

    # if titles_map.get(title):
    #     continue

    titles_map[title] = True

    year_search = re.search('[0-9]{4}', date_string)

    if not year_search:
        year_search = re.search('[0-9]{3}', date_string)

    event = {
        'title': title,
        'type': raw_event['relationships'][0]['entityName'],
        'summary': summaryObject(raw_event['valueUpdates']['Summary']),
        'imagePath': re.sub('attachments/', '', raw_event['imagePath']),
        'links': raw_event['links'],
        'startTS': raw_event['startTS'],
        'endTS': raw_event['endTS'],
        'dateString': date_string,
        'year': year_search.group(0),
        'durationString': raw_event['durationString'],
    }

    add_place(event)

    if is_bc:
        event['year'] = '-' + event['year']

    print(event)
    events.append(event)
    image = event['imagePath']
    image_file = 'docs/images/' + image
    if not os.path.isfile(image_file):
        img_data = requests.get(images_root + image).content
        with open(image_file, 'wb') as handler:
            print('downloading ' + image_file)
            handler.write(img_data)


with open('data/data.json', 'w') as html_file:
    html_file.write(json.dumps(events))

dateString = datetime.date.today().strftime('%Y-%m-%d')

with open('docs/all.html', 'w') as html_file:
     template = open('templates/template.html').read();
     html_file.write(template.replace('${date}', dateString).replace('${data}', json.dumps(events)))

with open('docs/places.html', 'w') as html_file:
     template = open('templates/places.html').read();
     html_file.write(template.replace('${date}', dateString).replace('${data}', json.dumps(events)))

with open('docs/people.html', 'w') as html_file:
     template = open('templates/template.html').read();
     html_file.write(template.replace('${date}', dateString).replace('${data}', json.dumps([p for p in events if p['type'] == 'People'])))

with open('docs/orgs.html', 'w') as html_file:
     template = open('templates/template.html').read();
     html_file.write(template.replace('${date}', dateString).replace('${data}', json.dumps([p for p in events if p['type'] == 'Organizations'])))

with open('docs/artifacts.html', 'w') as html_file:
     template = open('templates/template.html').read();
     html_file.write(template.replace('${date}', dateString).replace('${data}', json.dumps([p for p in events if p['type'] == 'Artifacts'])))

with open('data/places.txt', 'w') as html_file:
    text = '';
    for place in places:
        text += place + '\n'

    html_file.write(text)

