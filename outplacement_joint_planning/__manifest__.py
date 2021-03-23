
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
    'name': 'Outplacement - Joint Planning',
    'version': '12.0.1.0.5',
    'category': 'Outplacement',
    'description': """
    Module to handle the GUI for SubOrder (SV: Avrop ).
     v12.0.1.0.3 adds limitation for sending GP before day 6 in the service. AFC-1943\n
     v12.0.1.0.4 Fixed bugs in date comparison.\n
     v12.0.1.0.5 AFC-2002 changed calculation base for the 6th day in service\n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'outplacement',
        'res_joint_planning_af',
        'project',
        'outplacement_completion_report_ipf_client',
    ],
    'data': [
        'views/outplacement_view.xml',

    ],
    'installable': True,
}
