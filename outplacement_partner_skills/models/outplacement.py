# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = "outplacement"

    skills = fields.Many2many('hr.skill', string="All Skills")
    skill_id = fields.Char(string="Skill", related="skills.complete_name")

    other_experiences = fields.Many2many(comodel_name='outplacement.other_experiences', string="Other Experience")
    strengths = fields.Many2many(comodel_name='outplacement.strengths', string="Strengths")
    interests = fields.Many2many(comodel_name='outplacement.interests', string="Interests")
    partner_skill_ids = fields.One2many(
        string='Skills',
        comodel_name='hr.employee.skill',
        inverse_name='partner_id',
    )


class PartnerSkill(models.Model):
    _inherit = 'hr.employee.skill'

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
    )


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    skill = fields.Many2one(string="Skill", related="employee_skill_ids.skill_id")


class OtherExperiences(models.Model):
    _name = 'outplacement.other_experiences'
    _description = "Experiences"

    name = fields.Char(string="Experience")


class Strengths(models.Model):
    _name = 'outplacement.strengths'
    _description = "Strengths"

    name = fields.Char(string="Strengths")


class Interests(models.Model):
    _name = 'outplacement.interests'
    _description = "Interests"

    name = fields.Char(string="Interests")
