
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.modules.company.tests import CompanyTestMixin
from trytond.tests.test_tryton import ModuleTestCase


class CarrierSendShipmentsShippyproTestCase(CompanyTestMixin, ModuleTestCase):
    'Test CarrierSendShipmentsShippypro module'
    module = 'carrier_send_shipments_shippypro'


del ModuleTestCase
