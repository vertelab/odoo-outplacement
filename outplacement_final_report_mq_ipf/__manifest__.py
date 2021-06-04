# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Outplacement final report MQ/IPF-update dispatcher",
    'version': '12.0.0.1.2',
    'category': '',
    'description': """
To set up set system parameters:
outplacement_final_report_mq_ipf.mqhostport - ipfmq<1-3>-<environment>.arbetsformedlingen.se:61613
outplacement_final_report_mq_ipf.mquser - dafa
outplacement_final_report_mq_ipf.mqpwd
optional:
outplacement_final_report_mq_ipf.mqusessl - set to 0 if testing with activemq 
outplacement_final_report_mq_ipf.stomp_logger - DEBUG if debugging is needed



v12.0.0.1.1 - Fixed cron data\n
v12.0.0.1.2 - refactored code and bugfixes and better rejection message\n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base', 'outplacement_final_report'],
    'external_dependencies': {'python': ['stomp']},
    'data': ['data/cron.xml'],
    'application': False,
    'installable': True,
}
