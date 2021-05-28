{
    'name': 'Outplacement final report',
    'version': '12.0.0.2.1',
    'category': 'Outplacement',
    'description': """
Module to handle outplacement (Avrop) final reports.
===========================================================
v12.0.0.1.1 Translation and gui fix for eductation\n
v12.0.0.1.2 changed some field names\n
v12.0.0.1.3 Updated views, relations and translations\n
v12.0.0.1.4 Added timing dependent interruption text\n
v12.0.0.2.0 Added check and view for rejected final report\n
v12.0.0.2.1 Added Final report Approved date and Archive button.\n
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
