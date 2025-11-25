{
    'name': 'CustomModule',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Módulo para gestionar activos fijos con código QR',
    'author': 'Tu Empresa',
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
