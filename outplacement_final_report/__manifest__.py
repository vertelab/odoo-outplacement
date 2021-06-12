{
    'name': 'Outplacement final report',
    'version': '12.0.0.2.2',
    'category': 'Outplacement',
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'outplacement',
        'res_ssyk',
        'base_user_groups_dafa',
        'partner_education',
        'mail'
    ],
    'data': [
        'views/outplacement_view.xml',
        'security/ir.model.access.csv',
        'report/final_report_print.xml',
        'data/mail_data.xml'
    ],
    'installable': True,
}
