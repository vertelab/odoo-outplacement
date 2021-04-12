# -*- coding: UTF-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _inherit = 'outplacement'

    study_visit_ids = fields.One2many(comodel_name="outplacement.study_visit", inverse_name="outplacement_id")
    
    obstacle_reason = fields.Selection([
        ('Kan inte ta studielån', 'loan'), 
        ('På grund utav sjukdom', 'sickness'), 
        ('På grund utav ekonomisk situation', 'economy'), 
        ('Annat', 'Other')
        ])
    obstacle_motivation = fields.Text(string="Motivation")
    
    fr_send_date = fields.Date(string="Final report send date")
    fr_report_date = fields.Date(string="Reporting date")

    main_goal_id = fields.Many2one(comodel_name="outplacement.goal")
    alternative_goal_id = fields.Many2one(comodel_name="outplacement.goal")

    @api.constrains('study_visit_ids')
    @api.one
    def _constrain_study_visit_ids(self):
        if self.study_visit_ids and len(self.study_visit_ids) > 7:
            raise ValidationError(_('Number of study visits must not exceed 7'))


class OutplacementGoal(models.Model):
    _name = "outplacement.goal"

    field_of_work_id = fields.Many2one(
        comodel_name="res.ssyk", string="Field of work", required=True)
    # return codes for these two selections should be limited to search
    # ilike field_of_work.code
    job_id = fields.Many2one(comodel_name="res.ssyk", string="Job title", required=True)
    step_ids = fields.Many2many(
        comodel_name="outplacement.goal.step", string="Step")
    job_description = fields.Text(string="Job description", help="Describe work tasks the jobseeker wants to/can do") 
    matches_interest = fields.Boolean(string='Matches interest')
    matches_ability = fields.Boolean(string='Matches ability')
    market_demand = fields.Boolean(string='Market demand')
    complementing_education = fields.Boolean(string='Complementing education')
    complementing_experience = fields.Boolean(string='Complementing experience')
    other_motivation = fields.Boolean(string='Other')
    # should only be used if motivation is "other":
    free_text = fields.Char(string="Free text")

    @api.constrains('free_text')
    @api.one
    def _constrain_free_text(self):
        if self.free_text and len(self.free_text) > 100:
            raise ValidationError(_('Number of characters in the free text must not exceed 100'))
    
    @api.constrains('job_description')
    @api.one
    def _constrain_job_description(self):
        if self.job_description and len(self.job_description) > 2000:
            raise ValidationError(_('Number of characters in the job description field must not exceed 2000'))
    

    @api.constrains('step_ids')
    @api.one
    def _constrain_step_ids(self):
        if self.step_ids and (len(self.step_ids) < 1 or len(self.step_ids) > 10):
            raise ValidationError(_('Number of steps must not exceed 10, '
                                  'at least one step is required'))
    @api.multi
    def name_get(self):
        data = []
        for goal in self:
            display_value = goal.job_description if goal.job_description else goal.job_id
            data.append((goal.id, display_value))
        return data
    


class OutplacementGoalStep(models.Model):
    _name = "outplacement.goal.step"

    step_type = fields.Selection(selection=[
        ('Studera reguljär utbildning', 'study'),
        ('Lämpliga kompletterande insatser', 'fitting complementing efforts'),
        ('Annat', 'Other')], string="Type", required=True)  
    complementing_effort_type = fields.Selection(
        string="Complementing effort type", selection=[
            ('Studiemotiverande insats', 'study motivating effort'),
            ('Rusta inför arbete', 'prepare for work'),
            ('Matcha till arbete', 'match to work'),
            ('Utreda arbetsförmågan', 'evaluate ability to work'),
            ('Delta i en arbetsmarknadsutbildning/Praktik/Validering',
             'partake in education/internship/validation'),
            ('Svenskastudier inom valt område',
             'Swedish studies in chosen field'),
            ('Översättning av betyg', 'translation of grades'),
            ('Bedömning och komplettering av utländsk utbildning',
            'evaluation and complementation of foreign education'),
            ('Annat', 'Other')
            ])
    complementing_effort_description = fields.Char(
        string="Complementing effort")
    other_step_name = fields.Char(string="Name")
    level = fields.Char(string="Level")
    free_text = fields.Char(string="Free text")
    start_date = fields.Datetime(string="Start date")
    end_date = fields.Datetime(string="End date")

    @api.constrains('other_step_name')
    @api.one
    def _constrain_other_step_name(self):
        if self.other_step_name and len(self.other_step_name) > 1000:
            raise ValidationError(_('Number of characters in the name field must not exceed 1000'))
    
    @api.constrains('complementing_effort_description')
    @api.one
    def _constrain_complementing_effort_description(self):
        if self.complementing_effort_description and len(self.complementing_effort_description) > 1000:
            raise ValidationError(_('Number of characters in the description field must not exceed 1000'))
    
    @api.multi
    def name_get(self):
        data = []
        for goal in self:
            display_value = goal.step_type
            data.append((goal.id, display_value))
        return data


class OutplacementStudyVisit(models.Model):
    _name = "outplacement.study_visit"

    outplacement_id = fields.Many2one(comodel_name="outplacement", string="Outplacement")
    visit_selection = fields.Selection(string="Select organizer",
                                       selection=[
                                           ('workplace','Workplace'),
                                           ('education','Education organizer')
                                       ], default="education")
    name = fields.Char(string="Name")
    visit_type = fields.Char(string="Type")
    reasoning = fields.Text(string="Description")
