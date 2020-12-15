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

{
    'name': 'Sale outplacement',
    'version': '12.0.0.0.1',
    'category': 'Tools',
    'description': """Receives a suborder and automatically create sale.order 
    and outplacement.outplacement objects.""",
    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
    'depends': [
        'outplacement',
        'sale',
        'res_joint_planning_af',
        'sale_suborder_ipf_server',
        'project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product.xml',
        'views/outplacement_view.xml',
        'views/hr_department_view.xml',
        'views/product_product_views.xml',
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
