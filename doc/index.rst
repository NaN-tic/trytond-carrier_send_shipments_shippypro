Carrier Send Shipments Shippypro Module
#######################################

1. Autotenficación de ShippyPro:

Se debe generar un API Key, que seria el usuario (login) [1] y debemos usar la
contrasenya del usuario que nos hemos dado de alta. Con estos datos, debemos
crear un nuevo registro a "API transportistas" y el método "Shippypro".

A partir de "Nombre usuario" y "Contrasenya" de la configuración de
"API transportistas, se genera el base64 a partir de "<API KEY>:<PASSWORD>"
para la autentificación [2]

2. Configuración

A Shippypro debemos anadir los transportistas que trabajaremos y sus tarifas [3].
Una vez agregado los transportistas, en el apartado de API Key de shippypro.com,
en el apartado de "COURIER LIST" dispondremos de CarrierID y CarrierService.
Estos datos los deberemos copiar al ERP y se debe añadir en la información del
transportista o bien en la configuración de "API de transportista".

Si lo añadimos a la información del transportista, nos permite una sola "API key"
de Shippypro trabajar con varios transportistas. En cambio si lo añadimos solamente
en el apartado de "API transportistas" sólo nos permitirá trabajar en un solo transportista.

Los códigos de servicios que nos ofrecen "Shippypro" los debemos añadir como
servicios al ERP del transportista.

Además Shippypro nos obliga a dar un detalle del tipo de envío (ContentDescription).
Dicha información deberemos rellenar el campo "Content Description" de la
configuración de "API de transportistas".

Otros campos que son obligatorios y no configurables son:

- Incoterm: DAP por defecto.
- Parcels length: 1 por defecto
- Parcels width: 1 por defecto
- Parcels height: 1 por defecto
- Insurance: 0 por defecto
- CashOnDeliveryType: 0 por defecto # 0 = Cash, 1 = Cashier's check, 2 = Check

[1] https://www.shippypro.com/panel/apikeys.html
[2] https://www.shippypro.com/ShippyPro-API-Documentation/#authentication
[3] https://www.shippypro.com/panel/my-couriers.html
