# -*- coding: UTF-8 -*-

################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020 Vertel AB (<https://vertel.se>).
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
################################################################################
# Version format OdooMajor.OdooMinor.Major.Minor.Patch

{
    'name': 'Outplacement',
    'version': '12.0.1.2.3',
    'category': 'Outplacement',
    'description': """
	 Module to handle outplacement (Avrop)\n
	 v12.0.1.2.0 - changed version number to standard-format.\n
	 v12.0.1.2.1 - AFC-1116 Changes due to Performing Operations.\n
	 v12.0.1.2.3 - AFC-2120 Made some fields hidden outside of debug mode. \n
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base', 'hr', 'mail', 'partner_ssn'],
    'data': [
        'security/outplacement_security.xml',
        'security/ir.model.access.csv',
        'views/menu_item.xml',
        'views/outplacement_stage_view.xml',
        'views/outplacement_view.xml',
        'views/hr_department_view.xml',
        'views/res_partner_view.xml',
        'data/data.xml',
    ],
    'installable': True,
}
