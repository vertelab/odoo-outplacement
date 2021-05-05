# -*- coding: UTF-8 -*-
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'Outplacement Final Report send',
    'version': '12.0.0.1.5',
    'category': 'Outplacement',
    'description': """
This module adds a button to the outplacement interface that allows the sending of final reports.
===================================================================================================
v12.0.0.1.1 Fixed views and made error messages more readable\n
v12.0.0.1.2 Added warning stopping the user from sending too early\n
v12.0.0.1.3 added chatter message\n
v12.0.0.1.4 made it so that you can only send a day after service end\n
v12.0.0.1.5 Added reset for final report rejection check\n
""",

    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://vertel.se',
    'depends': ['outplacement_final_report_ipf_client', 'outplacement_final_report'],
    'data': [
        'views/outplacement_view.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
