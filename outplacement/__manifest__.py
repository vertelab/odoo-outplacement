{
    'name': 'Outplacement',
    'version': '12.0.1.2.0',
    'category': 'Outplacement',
    'description': """
	 Module to handle outplacement (Avrop).
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/outplacement_security.xml',
        'security/ir.model.access.csv',
        'views/menu_item.xml',
        'views/outplacement_stage_view.xml',
        'views/outplacement_view.xml',
        'views/hr_department_view.xml',
        'data/data.xml',
    ],
    'installable': True,
}
