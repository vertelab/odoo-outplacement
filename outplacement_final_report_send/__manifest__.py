# -*- coding: UTF-8 -*-
# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'Outplacement Final Report send',
    'version': '12.0.1.2.12',
    'category': 'Outplacement',
    'description': """
    v12.0.1.2.12 AFC-3334 - Fixed case with failing to send in endreport when is canceled.\n
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
