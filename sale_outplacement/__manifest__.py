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
    'name': 'Sale outplacement',
    'version': '12.0.1.1.1',
    'category': 'Outplacement',
    'maintainer': "Arbetsformedlingen",
    'author': "Vertel AB",
    'contributor': "Vertel, N-dev",
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'depends': [
        'outplacement',
        'sale',
        'res_joint_planning_af',
        'sale_suborder_ipf_server',
        'l10n_se',
        'project',
        'hr_skill',
        'partner_ssn',
        'res_interpreter_language',
        'sale_management',
        'base_user_groups_dafa',
        'account',
        'calendar',
        'hr_holidays'
    ],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'data/product.xml',
        'data/project.task.type.csv',
        'views/outplacement_view.xml',
        'views/product_views.xml',
        'views/project_views.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'images': [],
}
