{
    'name': 'CustomModule',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Modulo para gestionar activos fijos con codigo QR',
    'author': 'EMpresa Odoo Kreme',
    'depends': ['base', 'maintenance'],
    'data': [
        'security/ir.model.access.csv',
        'views/items_views.xml',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'Pillow'],
    },
    'installable': True,
    'application': False,
}
