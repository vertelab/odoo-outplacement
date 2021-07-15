# Version format OdooMajor.OdooMinor.Major.Minor.Patch
{
    'name': 'Deviation Report',
    'version': '12.0.0.1.6',
    'category': 'Outplacement',
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
