{
    'name': 'Outplacement final report',
    'version': '12.0.0.1.0',
    'category': 'Outplacement',
    'description': """
	 Module to handle outplacement (Avrop) final reports.
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['outplacement', 'res_sun', 'res_ssyk'],
    'data': [
        'views/outplacement_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
