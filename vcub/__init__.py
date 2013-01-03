# -*- coding: utf-8 -*-
import cherrypy
import os
import json
from dateutil.parser import parse
import datetime
import urllib2
from pykml import parser
from lxml import etree
from jinja2 import Environment, FileSystemLoader
current_dir = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(current_dir + '/templates'))


class Root:
    @cherrypy.expose
    def index(self):
        try:
            updated = parse(self.data_vcub['updated'])
            if (datetime.datetime.now() - updated) > datetime.timedelta(minutes=15):
                data = self.parse()
            else:
                data = self.data_vcub
        except:
            data = self.parse()
        tmpl = env.get_template('index.html')
        return tmpl.render(updated=parse(data['updated']), available=data['available'], traveling=data['traveling'], stations=json.dumps(data['stations']))

    data_vcub = {}

    def parse(self):
        available = 0
        traveling = 0
        live = self.vcub()
        with open(current_dir + '/doc.kml') as f:
            doc = parser.parse(f)
        placemarks = []
        for placemark in doc.getroot().Document.Folder.Placemark:
            coordinates = str(placemark.Point.coordinates).split(',')
            coordinates = [coordinates[1], coordinates[0]]
            data = {}
            for child in placemark.ExtendedData.SchemaData.SimpleData:
                data[child.get('name')] = child.text
            try:
                station = live[data['NOM']]
                for key in station.keys():
                    data[key] = station[key]
                if data['etat'] == 'DECONNECTEE':
                    data['class'] = 'offline'
                else:
                    if int(data['nbvelos']) == 0:
                        data['class'] = 'velos_red'
                        if int(data['nbplaces']) == 0:
                            data['class'] += ' places_red'
                        if int(data['nbplaces']) <= 3:
                            data['class'] += ' places_orange'
                        if int(data['nbplaces']) > 3:
                            data['class'] += ' places_green'
                    elif int(data['nbvelos']) <= 3:
                        data['class'] = 'velos_orange'
                        if int(data['nbplaces']) == 0:
                            data['class'] += ' places_red'
                        if int(data['nbplaces']) <= 3:
                            data['class'] += ' places_orange'
                        if int(data['nbplaces']) > 3:
                            data['class'] += ' places_green'
                    elif int(data['nbvelos']) > 3:
                        data['class'] = 'velos_green'
                        if int(data['nbplaces']) == 0:
                            data['class'] += ' places_red'
                        if int(data['nbplaces']) <= 3:
                            data['class'] += ' places_orange'
                        if int(data['nbplaces']) > 3:
                            data['class'] += ' places_green'
            except:
                data['class'] = 'offline'
            try:
                available += int(data['nbvelos'])
                traveling += int(data['NBSUPPOR']) - int(data['nbplaces'])
            except:
                pass
            placemarks.append({'coordinates': coordinates, 'data': data})
        self.data_vcub = {'available': available, 'traveling': traveling, 'stations': sorted(placemarks, key=lambda k: k['data']['NOM']), 'updated': placemarks[0]['data']['heure']}
        return self.data_vcub

    def vcub(self):
        request = urllib2.Request('http://data.lacub.fr/wfs?key=ULV4CR2TSD&SERVICE=WFS&VERSION=1.0.0&REQUEST=GetFeature&TYPENAME=CI_VCUB_P&SRSNAME=EPSG:3945', headers={'Accept': 'application/xml'})
        xml = etree.parse(urllib2.urlopen(request))
        stations = {}
        for station in xml.getroot().iter('{http://www.opengis.net/gml}featureMember'):
            for foo in station.iter('{http://mapserver.gis.umn.edu/mapserver}CI_VCUB_P'):
                data = {}
                for child in foo:
                    if child.tag == '{http://mapserver.gis.umn.edu/mapserver}ETAT':
                        data['etat'] = child.text
                    elif child.tag == '{http://mapserver.gis.umn.edu/mapserver}HEURE':
                        data['heure'] = child.text
                    elif child.tag == '{http://mapserver.gis.umn.edu/mapserver}NBPLACES':
                        data['nbplaces'] = child.text
                    elif child.tag == '{http://mapserver.gis.umn.edu/mapserver}NBVELOS':
                        data['nbvelos'] = child.text
                    elif child.tag == '{http://mapserver.gis.umn.edu/mapserver}NOM':
                        data['nom'] = child.text
                    elif child.tag == '{http://mapserver.gis.umn.edu/mapserver}TYPE':
                        data['type'] = child.text
                stations[data['nom']] = data
        return stations
