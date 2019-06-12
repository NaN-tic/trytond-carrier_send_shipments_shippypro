# This file is part of the carrier_send_shipments_shippypro module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval

__all__ = ['CarrierApi']


class CarrierApi(metaclass=PoolMeta):
    __name__ = 'carrier.api'
    shippypro_content_description = fields.Char('Content Description',
        states={
            'required': Eval('method') == 'shippypro',
        }, depends=['method'],
        help='Shippypro Content Description')
    shippypro_carrier_id = fields.Integer('Shippypro CarrierId')
    shippypro_carrier_name = fields.Char('Shippypro CarrierName')
    shippypro_document = fields.Selection([
            ('PDF', 'PDF'),
            ('ZPL', 'ZPL'),
        ], 'Shippypro Document',
        states={
            'required': Eval('method') == 'shippypro',
        }, depends=['method'])

    @staticmethod
    def default_shippypro_document():
        return 'PDF'

    @classmethod
    def get_carrier_app(cls):
        'Add Carrier MRW APP'
        res = super(CarrierApi, cls).get_carrier_app()
        res.append(('shippypro', 'Shippypro'))
        return res

    @classmethod
    def test_shippypro(cls, api):
        'Test shippypro connection'
        message = 'Connection unknown result'
        cls.raise_user_error(message)
