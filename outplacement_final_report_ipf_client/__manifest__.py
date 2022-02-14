# -*- coding: UTF-8 -*-
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'IPF Final Report Client',
    'version': '12.0.2.0.0',
    'category': 'Outplacement',
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['outplacement_final_report', 'api_ipf'],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
    ],
    'installable': True,
    'images': [
        'static/description/icon.png'
    ],
}
