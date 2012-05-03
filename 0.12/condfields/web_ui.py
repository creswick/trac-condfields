# Created by Noah Kantrowitz on 2007-05-05.
# Copyright (c) 2007 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.config import ListOption, BoolOption
from trac.web.api import IRequestFilter, IRequestHandler
from trac.web.chrome import ITemplateProvider, add_script, add_script_data
from trac.ticket.model import Type
from trac.ticket.api import TicketSystem
from trac.util.compat import sorted, set
from pkg_resources import resource_filename
import urllib

from pkg_resources import resource_filename

class CondFieldsModule(Component):
    """A filter to implement conditional fields on the ticket page."""

    implements(IRequestHandler, IRequestFilter, ITemplateProvider)

    include_std = BoolOption('condfields', 'include_standard', default='true',
                             doc='Include the standard fields for all types.')

    forced_fields = set(['type', 'summary', 'reporter', 'description',
                         'status', 'resolution', 'priority', 'time', 'changetime'])

    def __init__(self):
        # Initialize ListOption()s for each type.
        # This makes sure they are visible in IniAdmin, etc
        self.types = [t.name for t in Type.select(self.env)]
        for t in self.types:
            setattr(self.__class__, '%s_fields'%t, ListOption('condfields', t, doc='Fields to include for type "%s"'%t))

    def get_fields(self, ticket_type, all_fields, standard_fields):
        """Retrieve a dictionary mapping each field name to a boolean,
        indicating whether that field is valid for the specified
        ticket type."""
        fields = set(getattr(self, ticket_type+'_fields'))
        if self.include_std:
            fields.update(standard_fields)
        fields.update(self.forced_fields)
        return dict([
                (f, f in fields) for f in all_fields
                ])

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/condfields')

    def process_request(self, req):
        #self.log.debug("@ process_request")
        req.send_file(resource_filename(__name__, 'htdocs/condfields.js'), 'text/javascript')
        return ()

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, origData, content_type):
        if req.path_info.startswith('/newticket'):
            mode = 'new'
        elif req.path_info.startswith('/ticket/'):
            mode = 'view'
        else:
            return template, origData, content_type
        fieldData = {}
        fieldData['condfields'] = {}

        all_fields = []
        standard_fields = set()
        for f in TicketSystem(self.env).get_ticket_fields():
            all_fields.append(f['name'])
            if not f.get('custom'):
                standard_fields.add(f['name'])

        if 'owner' in all_fields:
            curr_idx = all_fields.index('owner')
            if 'cc' in all_fields:
                insert_idx = all_fields.index('cc')
            else:
                insert_idx = len(all_fields)
            if curr_idx < insert_idx:
                all_fields.insert(insert_idx, all_fields[curr_idx])
                del all_fields[curr_idx]

        for t in self.types:
            fieldData['condfields'][t] = self.get_fields(t, all_fields, standard_fields)

        self.log.debug(all_fields)
        self.log.info(standard_fields)

        fieldData['mode'] = mode
        fieldData['all_fields'] = list(all_fields)
        fieldData['ok_view_fields'] = sorted(set(all_fields) - self.forced_fields,
                                             key=lambda x: all_fields.index(x))
        fieldData['ok_new_fields'] = sorted((set(all_fields) - self.forced_fields) - set(['owner']),
                                            key=lambda x: all_fields.index(x))

        add_script_data(req, fieldData)
        add_script(req, '/condfields.js')
        return template, origData, content_type

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return [('condfields', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [ ]
