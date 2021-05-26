# -*- coding: UTF-8 -*-
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'IPF Final Report Client',
    'version': '12.0.0.1.8',
    'category': 'Outplacement',
    'description': """
This module adds the client config for final report.
====================================================================
V12.0.0.1.2 fixed some field names
V12.0.0.1.3 fixed values
V12.0.0.1.4 fixed a value, refactoring
V12.0.0.1.5 fixed values, added checks
V12.0.0.1.6 fixed the value "Kompletterar tidigare erfarenet" in "val_av_alternativt_mal_motivering" in "alternativt_mal" payload
v12.0.0.1.7 fixed the ability to send with no goals set when interrupted
v12.0.0.1.8 AFC-2368 Added 'Cancelled by AF' label in Outplacement kanban view if outplacement 'Interrupted'.
    """,

    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['outplacement_final_report'],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
