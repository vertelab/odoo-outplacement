# -*- coding: UTF-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    study_visit_ids = fields.Many2many(comodel_name="outplacement.study_visit")
    
    obstacle_reason = fields.Selection([
        ('loan', 'Kan inte ta studielån'), 
        ('sickness', 'På grund utav sjukdom'), 
        ('economy', 'På grund utav ekonomisk situation'), 
        ('other', 'Annat')
        ])
    obstacle_motivation = fields.Text(string="Motivation")
    
    send_date = fields.Datetime(string="Final report send date")
    report_date = fields.Datetime(string="Reporting date")

    main_goal_id = fields.Many2one(comodel_name="outplacement.goal")
    alternative_goal_id = fields.Many2one(comodel_name="outplacement.goal")


class OutplacementGoal(models.Model):
    _name = "outplacement.goal"

    field_of_work_id = fields.Many2one(
        comodel_name="res.ssyk", string="Field of work")
    # return codes for these two selections should be limited to search
    # ilike field_of_work.code
    job_id = fields.Many2one(comodel_name="res.ssyk", string="Job title")
    step_ids = fields.Many2many(
        comodel_name="outplacement.goal.step", string="Step")
    job_description = fields.Char(string="Job description") 
    matches_interest = fields.Boolean(string='Matches interest')
    matches_ability = fields.Boolean(string='Matches ability')
    market_demand = fields.Boolean(string='Market demand')
    complementing_education = fields.Boolean(string='Complementing education')
    complementing_experience = fields.Boolean(string='Complementing experience')
    other_motivation = fields.Boolean(string='Other')
    # should only be used if motivation is "other":
    free_text = fields.Char(string="Free text")


class OutplacementGoalStep(models.Model):
    _name = "outplacement.goal.step"

    step_type = fields.Selection(selection=[
        ('study', 'Studera och reguljär utbildning'),
        ('fitting complementing efforts', 'Lämpliga kompletterande insatser'),
        ('other', 'Other')], string="Type")  
    complementing_effort_type = fields.Selection(
        string="Complementing effort type", selection=[
            ('study motivating effort', 'Studiemotiverande insats'),
            ('prepare for work', 'Rusta inför arbete'),
            ('match to work', 'Matcha till arbete'),
            ('evaluate ability to work', 'Utreda arbetsförmågan'),
            ('partake in education/internship/validation',
             'Delta i en arbetsmarknadsutbildning/Praktik/Validering'),
            ('Swedish studies in chosen field',
             'Svenskastudier inom valt område'),
            ('translation of grades', 'Översättning av betyg'),
            ('evaluation and complementation of foreign education',
             'Bedömning och komplettering av utländsk utbildning'),
            ('other', 'Other')
            ])
    complementing_effort_description = fields.Char(
        string="Complementing effort")
    other_step_name = fields.Char(string="Name")
    other_step_level = fields.Char(string="Level")
    free_text = fields.Char(string="Free text")
    start_date = fields.Datetime(string="Start date")
    end_date = fields.Datetime(string="End date")


class OutplacementStudyVisit(models.Model):
    _name = "outplacement.study_visit"

    name = fields.Char(string="Name")
    visit_type = fields.Char(string="Type")  # needs values
    # should only be used if visit_type is "other".
    reasoning = fields.Text(string="Reasoning")
