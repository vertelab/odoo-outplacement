# -*- coding: UTF-8 -*-

###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020 - 2021 Vertel AB (<https://vertel.se>).
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
###############################################################################
# Version format OdooMajor.OdooMinor.Major.Minor.Patch

{
    'name': 'Outplacement DAFA',
    'version': '12.0.1.0.0',
    'category': 'Outplacement',
    'description': "Module to handle outplacement (Avrop) for "
                   "Arbetsförmedlingen DAFA""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['contacts', 'sale_outplacement', 'auth_user_rights_wizard'],
    'data': [
        'views/hr_employee_view.xml',
        'security/ir.model.access.csv',
        'security/outplacement_security.xml',
    ],
    'installable': True,
}
