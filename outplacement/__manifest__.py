{
    'name': 'Outplacement',
    'version': '12.0.0.1',
    'category': 'Human resources',
    'description': """
	 Module to handle outplacement (Avrop).
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_item.xml',
        'views/outplacement_stage_view.xml',
        'views/outplacement_view.xml',
        'data/data.xml',

    ],
    'installable': True,
}
