# This file is part of the carrier_send_shipments_shippypro module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields

__all__ = ['Carrier']


class Carrier(metaclass=PoolMeta):
    __name__ = 'carrier'
    shippypro_carrier_id = fields.Integer('Shippypro CarrierId')
    shippypro_carrier_name = fields.Char('Shippypro CarrierName')
