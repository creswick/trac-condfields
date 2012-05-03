# Created by Noah Kantrowitz on 2007-05-05.
# Copyright (c) 2007 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.config import ListOption, BoolOption
from trac.web.api import IRequestFilter, IRequestHandler
from trac.web.chrome import ITemplateProvider, add_script
from trac.ticket.model import Type
from trac.ticket.api import TicketSystem
from trac.util import sorted

try:
    set = set
except NameError:
    from sets import Set as set

class CondFieldsModule(Component):
    """A filter to implement conditional fields on the ticket page."""

    implements(IRequestHandler, IRequestFilter, ITemplateProvider)
    
    include_std = BoolOption('condfields', 'include_standard', default='true',
                             doc='Include the standard fields for all types.')
    
    forced_fields = set(['type', 'summary', 'reporter', 'description', 'status', 'resolution'])
    
    def __init__(self):
        # Initialize ListOption()s for each type.
        # This makes sure they are visible in IniAdmin, etc
        self.types = [t.name for t in Type.select(self.env)]
        for t in self.types:
            setattr(self.__class__, '%s_fields'%t, ListOption('condfields', t, doc='Fields to include for type "%s"'%t))

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/condfields')

    def process_request(self, req):
        mode = req.args.get('mode', 'view')
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
            fields = set(getattr(self, t+'_fields'))
            if self.include_std:
                fields.update(standard_fields)
            fields.update(self.forced_fields)
            req.hdf['condfields.types.%s'%t] = dict([
                (f, f in fields) for f in all_fields
            ])
        req.hdf['condfields.mode'] = mode
        req.hdf['condfields.all_fields'] = list(all_fields)
        req.hdf['condfields.ok_fields'] = sorted(set(all_fields) - self.forced_fields, key=lambda x: all_fields.index(x))
        return 'condfields.cs', 'text/javascript'

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
            
    def post_process_request(self, req, template, content_type):
        if req.path_info.startswith('/newticket') or req.path_info.startswith('/ticket/'):
            add_script(req, 'condfields/jquery.js')
            idx = 0
            while True:
                js = req.hdf.get('chrome.scripts.%i.href'%idx)
                if not js:
                    break
                idx += 1
            req.hdf['chrome.scripts.%i' % idx] = {
                'href': req.href.condfields('condfield.js', mode=req.path_info.startswith('/newticket') and 'new' or 'view'), 
                'type': 'text/javascript',
            }
        return template, content_type

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('condfields', resource_filename(__name__, 'htdocs'))]
            
    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]