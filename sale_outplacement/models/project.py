import base64
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    outplacement_id = fields.Many2one(
        comodel_name='outplacement',
        string='Outplacement',
        index=True,
        default=lambda self: self.env.context.get('default_project_id'))
    activity_id = fields.Many2one('res.joint_planning', 'Activity')
    joint_planing_type = fields.Selection([
        ('kvl', 'KVL'),
        ('preplaning', 'Preplaning'),
        ('endraport', 'Endraport'),
    ], 'JP_Type')
    task_type = fields.Selection(selection=[('mandatory', 'Mandatory'),
                                            ('optional', 'Optional'), ],
                                 string='Task Type', )
    
    @api.model
    def init_joint_planning(self,outplacement_id):
        for task in self.env['res.joint_planning'].search([],order='sequence'):
            self.env['project.task'].create({
                'outplacement_id': outplacement_id,
                'joint_planing_type': 'preplaning',
                'task_type': task.task_type,
                'activity_id': task.id,
                'name': task.name,
                'color': task.color,
                'planned_hours': task.planned_hours,
            })

    @api.model
    def init_joint_planning_stages(self,outplacement_id):
        for stage in self.env['project.task.type'].search([('is_outplacement','=',True)]):
            stage.outplacement_ids = [(4, outplacement_id)]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages = super(ProjectTask,self)._read_group_stage_ids(stages, domain, order)
        if [elem for elem in domain if 'outplacement_id' in elem]:
            return stages.search([('is_outplacement', '=', True)])
        return stages
        
        
class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    def _get_default_outplacement_ids(self):
        default_outplacement_id = self.env.context.get('default_outplacement_id')
        return [default_outplacement_id] if default_outplacement_id else None
        fields.Many2many(comodel_name='_',string='_') # relation|column1|column2
    outplacement_ids = fields.Many2many(
        comodel_name='outplacement',
        relation='outplacement_task_type_rel',
        column1='type_id', 
        column2='outplacement_id',
        string='Outplacement',
        default=_get_default_outplacement_ids)
    is_outplacement = fields.Boolean(string='Is Outplacement')
    
    @api.multi
    def unlink(self):
        stages = self
        default_project_id = self.env.context.get('default_outplacement_id')
        if default_project_id:
            shared_stages = self.filtered(lambda x: len(x.outplacement_ids) > 1 and default_outplacement_id in x.outplacement_ids.ids)
            tasks = self.env['project.task'].with_context(active_test=False).search([('outplacement_id', '=', default_outplacement_id), ('stage_id', 'in', self.ids)])
            if shared_stages and not tasks:
                shared_stages.write({'outplacement_ids': [(3, default_outplacement_id)]})
                stages = self.filtered(lambda x: x not in shared_stages)
        return super(ProjectTaskType, stages).unlink()
