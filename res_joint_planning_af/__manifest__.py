
# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
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
    'name': 'Res Joint Planning',
    'version': '12.0.0.1.2',
    'category': 'Outplacement',
    'description': """
	 Module to handle outplacement (Avrop).\n
	 This module handles the Activity template (project.task)
    12.0.0.1.2: ACL-Made it possible for normal users to send GP.
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['outplacement'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_joint_planning_view.xml',
        'data/data.xml',

    ],
    'installable': True,
}
