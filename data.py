accepted_user = {
    "name": "Harold Lee",
    "password": "Ss123456",
}

unaccepted_users = [
    # password too short
    {
        "name": "Harold Lee",
        "password": "Ss12",
    },
    # password too long
    {
        "name": "Harold Lee",
        "password": "Ss12345678901234567890123456789012",
    },
    # password not contains digits
    {
        "name": "Harold Lee",
        "password": "Ssqwertyu",
    },
    # password not contains lowercase letters
    {
        "name": "Harold Lee",
        "password": "QWERTIN123",
    },
    # password not contains uppercase letters
    {
        "name": "Harold Lee",
        "password": "qjdsabj123",
    },
    # name too short
    {
        "name": "test",
        "password": "Ss123456",
    },
    # name too long
    {
        "name": "test test test test test test test test test test",
        "password": "Ss123456",
    },
    # no password
    {
        "name": "Harold Lee",
    },
    # no name
    {
        "password": "Ss123456",
    },
]

accepted_products = [
    # complete
    {
        "material": "material#1",
        "name": "name#1",
        "spec": "spec#1",
        "unit": "piece",
        "quantity": "10",
    },
    # material is null
    {
        "material": None,
        "name": "name#2",
        "spec": "spec#2",
        "unit": "piece",
        "quantity": "10",
    },
    # no material
    {
        "name": "name#3",
        "spec": "spec#3",
        "unit": "piece",
        "quantity": "10",
    },
    # no quantity
    {
        "material": "material#4",
        "name": "name#4",
        "spec": "spec#4",
        "unit": "piece",
    },
    # material is empty string
    {
        "material": "",
        "name": "name#5",
        "spec": "spec#5",
        "unit": "piece",
    },
    # quantity is null
    {
        "material": "material#6",
        "name": "name#6",
        "spec": "spec#6",
        "unit": "piece",
        "quantity": None,
    },
]

unaccepted_products = [
    # quantity is not a number
    {
        "material": "material#1",
        "name": "name#1",
        "spec": "spec#1",
        "unit": "piece",
        "quantity": "hello",
    },
    # no name
    {
        "material": "material#1",
        "spec": "spec#1",
        "unit": "piece",
    },
    # no spec
    {
        "material": "material#1",
        "spec": "spec#1",
        "unit": "piece",
    },
    # no unit
    {
        "material": "material#1",
        "name": "name#1",
        "spec": "spec#1",
    },
]

accepted_partners = [
    {
        "name": "partner#1",
        "address": "address#1",
        "phone": "phone#1",
        "folder": "folder#1",
    },
    # no address, address, folder
    {
        "name": "partner#2",
    },
    # address, address, folder are null
    {
        "name": "partner#3",
        "address": None,
        "phone": None,
        "folder": None,
    },
]

unaccepted_partners = [
    # no name
    {
        "address": "address#1",
        "phone": "phone#1",
        "folder": "folder#1",
    },
]

accepted_invoices = [
    # normal
    {
        "date": "2020-01-01",
        "type": 0,
        "partner": {"name": "partner#1"},
        "invoiceItems": [],
        "amount": "100",
        "prepayment": "0",
        "payment": "100",
        "deliveryStatus": 0,
        "order": None,
    },
    # no order
    {
        "date": "2020-01-01",
        "type": 0,
        "partner": {"name": "partner#2"},
        "invoiceItems": [],
        "amount": "100",
        "prepayment": "0",
        "payment": "100",
        "deliveryStatus": 0,
    },
]

unaccepted_invoices = [
    # order id is null
    {
        "date": "2020-01-01",
        "type": 0,
        "partner": {"name": "partner#1"},
        "invoiceItems": [],
        "amount": "100",
        "prepayment": "0",
        "payment": "100",
        "deliveryStatus": 0,
        "order": {"id": None},
    },
    # refund but no order
    {
        "date": "2020-01-01",
        "type": 2,
        "partner": {"name": "partner#1"},
        "invoiceItems": [],
        "amount": "100",
        "prepayment": "0",
        "payment": "100",
        "deliveryStatus": 0,
        "order": None,
    },
    {
        "date": "2020-01-01",
        "type": 2,
        "partner": {"name": "partner#1"},
        "invoiceItems": [],
        "amount": "100",
        "prepayment": "0",
        "payment": "100",
        "deliveryStatus": 0,
    },
    # no type
    {
        "date": "2020-01-01",
        "partner": {"name": "partner#1"},
        "invoiceItems": [],
        "amount": "100",
        "prepayment": "0",
        "payment": "100",
        "deliveryStatus": 0,
    },
]

accepted_inventory_records = [
    {
        "type": 0,
        "quantity": "10",
        "weight": None,
        "remark": "remark#1",
        "status": 0,
        "completedAt": "2025-01-23T13:50:59Z",
        "operator": "operator",
    }
]
