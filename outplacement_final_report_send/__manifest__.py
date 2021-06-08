# -*- coding: UTF-8 -*-
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'Outplacement Final Report send',
    'version': '12.0.0.1.0',
    'category': 'Outplacement',
    'description': """This module adds a button to the outplacement interface that allows the sending of final reports.""",

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
