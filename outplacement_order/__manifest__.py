# -*- coding: UTF-8 -*-

###############################################################################
#
#    OpenERP, Open Source Management Solution
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
    "name": "Outplacement Order (Ordertjansten Order)",
    "version": "12.0.1.0.4",
    "category": "Outplacement",
    "description": """
Outplacement Order (Ordertjansten Order)\n
===============================================================================\n
This module listen for updates for an order\n
v12.0.1.0.3: Versions before version handling\n
v12.0.1.0.4 AFC-2105: added update to field service_end_date when interupting outplacement\n
""",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se",
    "depends": [
        "outplacement",
        "sale_showorder_ipf_client",
    ],
    "data": [
        "data/cron.xml",
        "data/data.xml",
        "views/outplacement_stage_view.xml",
    ],
    "installable": True,
    "images": ["static/description/img.png"],
}
