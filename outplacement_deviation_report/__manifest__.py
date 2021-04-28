# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'Deviation Report',
    'version': '12.0.0.1.4',
    'category': 'Outplacement',
    "description": """
Outplacement Deviation Report\n
===============================================================================\n
v12.0.0.1.1: Versions before version handling\n
v12.0.0.1.2 AFC-2104: Changed "sent"-message in chatter box\n
v12.0.0.1.3 improved error messages
v12.0.0.1.4 added checks and error messages
""",
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
    'depends': [
        'outplacement',
        'outplacement_deviationreport_ipf_client',
        'af_security',
        'sale_outplacement',
        'partner_legacy_id',
        'partner_firstname',
    ],
    'data': [
        'wizards/deviation_report_wizard.xml',
        'views/outplacement_view.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
