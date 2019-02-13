# -*- coding: utf-8 -*-
{
    'name': "Neonety ajustes ( Directorio de contactos personalizado )",

    'summary': """
        Personalización del directorio de contactos basados en la distribución geográfica
        de Panamá.""",

    'description': """
        Personalización del directorio de contactos basados en la distribución geográfica
        de Panamá
    """,

    'author': "Neonety & TecnoSoluciones Jurado FP",
    'website': "http://www.tecnosolucionesjurado.com.ve",
    'category': 'Sales',
    'version': '1.11',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'product', 'contacts'],

    # always loaded
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/neonety_partner_concepts_data.xml',
        'views/neonety_partner_concepts_view.xml',
        'views/neonety_addresses_data.xml',
        'views/neonety_addresses_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}