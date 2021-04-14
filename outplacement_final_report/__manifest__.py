{
    'name': 'Outplacement final report',
    'version': '12.0.0.1.3',
    'category': 'Outplacement',
    'description': """
Module to handle outplacement (Avrop) final reports.
===========================================================
v12.0.0.1.1 Translation and gui fix for eductation
v12.0.0.1.2 changed some field names
v12.0.0.1.3 Updated views, relations and translations
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'outplacement', 
        'res_ssyk',
        'base_user_groups_dafa',
        'partner_education'
        ],
    'data': [
        'views/outplacement_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
