# This file is part of the carrier_send_shipments_shippypro module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields
from trytond.modules.carrier_send_shipments.tools import unaccent, unspaces
import requests
import logging
import time
import tempfile
import base64
import json

__all__ = ['ShipmentOut']
logger = logging.getLogger(__name__)

def shippypro_header(api):
    return base64.b64encode('%s:%s' % (api.username, api.password))

def shippypro_send(api, values):
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic %s' % shippypro_header(api)
    }
    return requests.post('https://www.shippypro.com/api',
        data=values, headers=headers, timeout=api.timeout)


class ShipmentOut:
    __metaclass__ = PoolMeta
    __name__ = 'stock.shipment.out'

    shippypro_neworder_id = fields.Char('Shippypro order ref.')

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        cls._error_messages.update({
            'shippypro_carrier_and_service': ('Please, configure a CarrierID, '
                'CarrierName or Service in Shippypro or carrier configuration.'),
            })

    @classmethod
    def shippypro_get_parcels(cls, api, shipment, weight):
        # Default parcels
        parcels = {}
        parcels["length"] = 1
        parcels["width"] = 1
        parcels["height"] = 1
        parcels["weight"] = weight
        return [parcels]

    @classmethod
    def send_shippypro(cls, api, shipments):
        '''
        Send shipments out to shippypro
        :param api: obj
        :param shipments: list
        Return references, labels, errors
        '''
        pool = Pool()
        CarrierApi = pool.get('carrier.api')
        ShipmentOut = pool.get('stock.shipment.out')
        Uom = pool.get('product.uom')

        references = []
        labels = []
        errors = []

        default_service = CarrierApi.get_default_carrier_service(api)

        to_write = []
        for shipment in shipments:
            service = shipment.carrier_service or shipment.carrier.service or default_service

            carrier_id = shipment.carrier.shippypro_carrier_id or api.shippypro_carrier_id
            carrier_name = shipment.carrier.shippypro_carrier_name or api.shippypro_carrier_name
            if not carrier_id or not carrier_name or not service:
                message = cls.raise_user_error('shippypro_carrier_and_service', {},
                    raise_exception=False)
                errors.append(message)
                continue

            code = shipment.code
            currency = shipment.currency.code
            if api.reference_origin and hasattr(shipment, 'origin'):
                if shipment.origin:
                    code = shipment.origin.rec_name
                    if hasattr(shipment.origin, 'currency'):
                        currency = shipment.origin.currency.code

            notes = ''
            if shipment.carrier_notes:
                notes = '%s\n' % shipment.carrier_notes

            weight = 1.0
            if api.weight and hasattr(shipment, 'weight_func'):
                weight = shipment.weight_func
                weight = 1.0 if weight == 0.0 else weight

                if api.weight_api_unit:
                    if shipment.weight_uom:
                        weight = Uom.compute_qty(
                            shipment.weight_uom, weight, api.weight_api_unit)
                    elif api.weight_unit:
                        weight = Uom.compute_qty(
                            api.weight_unit, weight, api.weight_api_unit)

            price_ondelivery = 0
            if shipment.carrier_cashondelivery:
                price_ondelivery = shipment.carrier_cashondelivery_price

            if shipment.warehouse.address:
                waddress = shipment.warehouse.address
            else:
                waddress = api.company.party.addresses[0]

            values = {}
            values["Method"] = "Ship"

            params = {}
            params["to_address"] = {}
            params["to_address"]["name"] = unaccent(shipment.customer.name)[:35] # Name cannot exceed 35 characters
            params["to_address"]["company"] = ""
            params["to_address"]["street1"] = unaccent(shipment.delivery_address.street)
            params["to_address"]["street2"] = ""
            params["to_address"]["city"] = unaccent(shipment.delivery_address.city)
            params["to_address"]["state"] = (shipment.delivery_address.subdivision.code
                if shipment.delivery_address.subdivision else "")
            params["to_address"]["zip"] = shipment.delivery_address.zip
            params["to_address"]["country"] = (shipment.delivery_address.country
                and shipment.delivery_address.country.code or "")
            params["to_address"]["phone"] = unspaces(shipment.mobile or shipment.phone or api.phone)
            params["to_address"]["email"] = unspaces(shipment.email)

            params["from_address"] = {}
            params["from_address"]["name"] = unaccent(api.company.party.name)
            params["from_address"]["company"] = unaccent(api.company.party.name)
            params["from_address"]["street1"] = unaccent(waddress.street)
            params["from_address"]["street2"] = ""
            params["from_address"]["city"] = unaccent(waddress.city)
            params["from_address"]["state"] = (waddress.subdivision.code
                if waddress.subdivision else "")
            params["from_address"]["zip"] = unaccent(waddress.zip)
            params["from_address"]["country"] = (waddress.country.code
                if waddress.country else "")
            params["from_address"]["phone"] = (unspaces(api.phone)
                if api.phone else "")
            params["from_address"]["email"] = (unspaces(api.email)
                if api.email else "")

            parcels = {}
            parcels["length"] = 1 # set hardcode value; required
            parcels["width"] = 1 # set hardcode value; required
            parcels["height"] = 1 # set hardcode value; required
            parcels["weight"] = weight
            params["parcels"] = cls.shippypro_get_parcels(api, shipment, weight)

            params["TotalValue"] = "%s %s" % (shipment.total_amount, currency)
            params["TransactionID"] = "%s" % code
            params["ContentDescription"] = api.shippypro_content_description
            params["Insurance"] = 0 # set hardcode value; required
            params["InsuranceCurrency"] = currency
            params["CashOnDelivery"] = float(price_ondelivery) if price_ondelivery else 0
            params["CashOnDeliveryCurrency"] = currency
            params["CashOnDeliveryType"] = 0 # 0 = Cash, 1 = Cashier's check, 2 = Check
            params["CarrierName"] = carrier_name
            params["CarrierService"] = service.code
            params["CarrierID"] = carrier_id
            params["OrderID"] = shipment.id
            params["RateID"] = ""
            params["Incoterm"] = "DAP" # set hardcode value; required
            params["BillAccountNumber"] = ""
            params["Note"] = unaccent(notes)
            params["Async"] = False

            values["Params"] = params

            response = shippypro_send(api, json.dumps(values))
            results = json.loads(response.text)
            if not response.status_code == 200:
                message = '%s %s' % (response.status_code, results.get('Error'))
                errors.append(message)
                continue

            shippypro_errors = results.get('Error')
            if shippypro_errors:
                errors.append(shippypro_errors)
                continue

            shippypro_errors = results.get('ErrorMessage')
            if shippypro_errors and results.get('Status') != '1':
                logger.error(shippypro_errors)
                continue

            validation_errors = results.get('ValidationErrors')
            if validation_errors:
                errors.append(validation_errors)

            carrier_tranking_ref = cls.get_carrier_tracking_reference(results)
            shippypro_neworder_id = cls.get_shippypro_new_order_id(results)
            if carrier_tranking_ref:
                values = {
                    'carrier_tracking_ref': carrier_tranking_ref,
                    'carrier_service': service,
                    'carrier_delivery': True,
                    'carrier_send_date': ShipmentOut.get_carrier_date(),
                    'carrier_send_employee': ShipmentOut.get_carrier_employee() or None,
                    }
                shipment.carrier_tracking_ref = carrier_tranking_ref
                shipment.shippypro_order_ref = shippypro_neworder_id
                to_write.extend(([shipment], values))
                logger.info('Send shipment %s' % (shipment.code))
                references.append(shipment.code)
                # add time sleep because we need the signal shippypro
                # and carrier return the label
                time.sleep(10)
                labels += cls.print_labels_shippypro(api, [shipment])
            else:
                logger.error('Not send shipment %s.' % (shipment.code))

        if to_write:
            cls.write(*to_write)

        return references, labels, errors

    @classmethod
    def get_carrier_tracking_reference(cls, results):
        return results.get('NewOrderID')

    @classmethod
    def get_shippypro_new_order_id(cls, results):
        return results.get('NewOrderID')

    @classmethod
    def print_labels_shippypro(cls, api, shipments):
        '''
        Get labels from shipments out from Shippypro
        '''
        labels = []
        dbname = Transaction().cursor.dbname

        to_write = []
        for shipment in shipments:
            if not shipment.carrier_tracking_ref:
                logger.error(
                    'Shipment %s has not been sent by Shippypro.'
                    % (shipment.code))
                continue

            reference = shipment.carrier_tracking_ref
            document = api.shippypro_document or 'PDF'

            values = {}
            values["Method"] = "GetOrder"
            params = {}
            params['OrderID'] = shipment.carrier_tracking_ref
            values["Params"] = params

            response = shippypro_send(api, json.dumps(values))
            results = json.loads(response.text)
            if not response.status_code == 200:
                message = '%s %s' % (response.status_code, results.get('Error'))
                logger.error(message)
                continue

            shippypro_errors = results.get('ErrorMessage')
            if shippypro_errors and results.get('Status') != '1':
                logger.error(shippypro_errors)
                continue

            label_url = results.get('LabelURL')
            if label_url:
                response2 = requests.get(label_url[0], timeout=None)
                if not response2.status_code == 200:
                    message = '%s %s' % (response2.status_code,
                        'Error from Shippypro when get the label')
                    logger.error(message)
                    continue

                with tempfile.NamedTemporaryFile(
                        prefix='%s-shippypro-%s-' % (dbname, reference),
                        suffix='.%s' % document, delete=False) as temp:
                    temp.write(response2.content)
                logger.info(
                    'Generated tmp label %s' % (temp.name))
                temp.close()
                labels.append(temp.name)
                to_write.extend(([shipment], {'carrier_printed': True}))

        if to_write:
            cls.write(*to_write)

        return labels
