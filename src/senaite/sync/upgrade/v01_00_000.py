# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.SYNC
#
# Copyright 2018 by it's authors.

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import api
from bika.lims import logger
from bika.lims.upgrade import upgradestep

version = '1.0.0'
profile = 'profile-{senaite.sync}:default'


@upgradestep('senaite.sync', version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    fields_to_update = ['expirationDate', 'effectiveDate']
    skip = ['Sample', 'Doctor', 'Instrument', 'Calculation',
            'InstrumentCertification', 'Contact', 'LabContact', 'Batch',
            'ARReport']
    pc = api.get_tool("portal_catalog", portal)
    brains = pc(is_folderish=True)
    for brain in brains:
        if brain.portal_type in skip:
            continue
        obj = brain.getObject()
        logger.info("Handling {}".format(repr(obj)))
        schema = obj.Schema()
        fields = dict(zip(schema.keys(), schema.fields()))
        for field_name in fields_to_update:
            field = fields.get(field_name)
            field.set(obj, None)
        obj.reindexObject()
        logger.info('Done: {}'.format(obj))
    return True
