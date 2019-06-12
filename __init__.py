# This file is part carrier_send_shipments_shippypro module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import api
from . import carrier
from . import shipment


def register():
    Pool.register(
        api.CarrierApi,
        carrier.Carrier,
        shipment.ShipmentOut,
        module='carrier_send_shipments_shippypro', type_='model')
