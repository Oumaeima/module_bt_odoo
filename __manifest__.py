# -*- coding: utf-8 -*-

{
    'name': 'GMAO',
    'version': '1.0',
    'sequence': 10,
    'category': 'Maintenance',
    'description': """
    Advenced Management of Maintenance Operations (GMAO)""",
    'depends': ['maintenance','mail'],
    'summary': 'Advenced Management of Maintenance Operations (GMAO)',
    'data': [
        'data/bt_stage_data.xml', 
        'data/bt_cron.xml',
        'views/bt_views.xml',
        'views/gmao_menus.xml',
        'report/bt_report.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {
    },
    'license': 'LGPL-3',
}
