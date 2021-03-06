from canari.maltego.entities import Hashtag
from canari.maltego.transform import Transform
# from canari.framework import EnableDebugWindow
from MISP_maltego.transforms.common.entities import MISPEvent, MISPObject
from MISP_maltego.transforms.common.util import get_misp_connection, attribute_to_entity, event_to_entity, galaxycluster_to_entity, object_to_entity, object_to_attributes
import json

__author__ = 'Christophe Vandeplas'
__copyright__ = 'Copyright 2018, MISP_maltego Project'
__credits__ = []

__license__ = 'AGPLv3'
__version__ = '0.1'
__maintainer__ = 'Christophe Vandeplas'
__email__ = 'christophe@vandeplas.com'
__status__ = 'Development'


# @EnableDebugWindow
class EventToAttributes(Transform):
    """Expands an event to attributes, objects, tags and galaxies."""

    # The transform input entity type.
    input_type = MISPEvent
    description = 'Expands an Event to Attributes, Tags, Galaxies and related events'

    def do_transform(self, request, response, config):
        maltego_misp_event = request.entity
        # print(dir(maltego_misp_event))
        misp = get_misp_connection(config)
        event_json = misp.get_event(maltego_misp_event.id)  # FIXME get it without attachments
        # print(json.dumps(event_json, sort_keys=True, indent=4))
        if not event_json.get('Event'):
            return response
        for e in event_json['Event']['RelatedEvent']:
            response += event_to_entity(e)
        for a in event_json['Event']["Attribute"]:
            for entity in attribute_to_entity(a):
                if entity:
                    response += entity
        for o in event_json['Event']['Object']:
            # LATER unfortunately we cannot automatically expand the objects
            response += object_to_entity(o)
        for g in event_json['Event']['Galaxy']:
            for c in g['GalaxyCluster']:
                response += galaxycluster_to_entity(c)
        if 'Tag' in event_json['Event']:
            for t in event_json['Event']['Tag']:
                # ignore all misp-galaxies
                if t['name'].startswith('misp-galaxy'):
                    continue
                response += Hashtag(t['name'])
        return response

    def on_terminate(self):
        """This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms. It can be excluded if you don't need it."""
        pass


# @EnableDebugWindow
class ObjectToAttributes(Transform):
    """"Expands an object to its attributes"""
    input_type = MISPObject
    description = 'Expands an Obect to Attributes'

    def do_transform(self, request, response, config):
        maltego_object = request.entity
        misp = get_misp_connection(config)
        event_json = misp.get_event(maltego_object.event_id)
        for o in event_json['Event']['Object']:
            if o['uuid'] == maltego_object.uuid:
                for entity in object_to_attributes(o):
                    if entity:
                        response += entity

        return response
