# -*- coding: UTF-8 -*-
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'IPF Final Report Client',
    'version': '12.0.0.1.2',
    'category': 'Outplacement',
    'description': """
This module adds the client config for final report.
====================================================================
V12.0.0.1.2 fixed some field names
    """,

    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['outplacement', 'res_joint_planning_af'],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
