# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.SYNC
#
# Copyright 2018 by it's authors.

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims import logger
from bika.lims.utils import changeWorkflowState
from bika.lims.upgrade import upgradestep

version = '1.0.0'
profile = 'profile-{senaite.sync}:default'


@upgradestep('senaite.sync', version)
def upgrade(tool):

    portal = aq_parent(aq_inner(tool))
    fields_to_update = ['expirationDate', 'effectiveDate']
    types = ['Doctor', 'Instrument', 'Calculation',
            'InstrumentCertification', 'Contact', 'LabContact']
    pc = api.get_tool("portal_catalog", portal)
    brains = pc(is_folderish=True, portal_type={"query": types,
                                                "operator": "or"})
    for brain in brains:
        obj = brain.getObject()
        logger.info("Handling {}".format(repr(obj)))
        schema = obj.Schema()
        fields = dict(zip(schema.keys(), schema.fields()))
        for field_name in fields_to_update:
            field = fields.get(field_name)
            field.set(obj, None)
        obj.reindexObject()
        logger.info('Done: {}'.format(obj))

    logger.info("*** Permissions fixed! ***")

    ar_c = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING, portal)
    ars = ar_c(review_state='to_be_verified')
    logger.info("Walking through {} AR's in 'to_be_verified' state".format(len(ars)))
    for ar in ars:
        obj = ar.getObject()
        ans = obj.getAnalyses()
        for an in ans:
            if an.review_state == 'sample_received':
                logger.info("Fixing review_state of {} ".format(repr(obj)))
                changeWorkflowState(obj,'bika_ar_workflow', "sample_received")
                obj.reindexObject()
                break

    logger.info("*** AR states fixed! ***")
    return True
