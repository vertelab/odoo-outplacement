import base64
import logging
from odoo.exceptions import ValidationError, UserError

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo import tools, _

_logger = logging.getLogger(__name__)

xmlid_module = '__outplacement__'


class ProjectTask(models.Model):
    _inherit = "project.task"

    start_date = fields.Datetime(string="Start date")
    end_date = fields.Datetime(string="End date")
    child_end_date = fields.Datetime(string="Child End date",
                                     related="end_date",
                                     readonly=False)
    child_start_date = fields.Datetime(string="Child Start date",
                                       related="start_date",
                                       readonly=False)
    duration = fields.Float(string="Duration")
    instructions = fields.Text(string="Instructions", readonly=True)
    outplacement_id = fields.Many2one(
        comodel_name="outplacement",
        string="Outplacement",
        index=True,
        # default=lambda self: self.env.context.get("default_project_id"),
        default=lambda self: self.env.context.get("default_outplacement_id"),
    )
    order_id_origin = fields.Char(related='outplacement_id.order_id_origin')
    outplacement_name = fields.Char(related='outplacement_id.name')
    performing_operation_id = fields.Many2one('performing.operation',
                                              related='outplacement_id.performing_operation_id')
    partner_name = fields.Char(related='outplacement_id.partner_name')
    employee_id = fields.Many2one('hr.employee', related='outplacement_id.employee_id')
    activity_id = fields.Many2one("res.joint_planning", "Activity")
    joint_planing_type = fields.Selection(
        [
            ("kvl", "KVL"),
            ("preplaning", "Preplaning"),
            ("endraport", "Endraport"),
        ],
        "JP_Type",
    )
    task_type = fields.Selection(
        selection=[
            ("mandatory", "Mandatory"),
            ("optional", "Optional"),
        ],
        string="Task Type",
    )

    @api.one
    @api.constrains('parent_id')
    def _constrain_same_outplacement(self):
        if self.parent_id:
            if self.outplacement_id != self.parent_id.outplacement_id:
                raise ValidationError(_("Parent activity must have the same outplacement as its children."))

    @api.onchange('start_date', 'end_date')
    def _compute_duration(self):
        if self.start_date and self.end_date:
            diff = self.end_date - self.start_date
            duration = round(diff.total_seconds() / 3600, 2)
            self.duration = duration

    @api.model
    def init_joint_planning(self, outplacement_id):
        for task in self.env["res.joint_planning"].search([], order="sequence"):
            try:
                stage_todo = self.env.ref(".".join([xmlid_module, 'stage_todo']))
                stage_optional = self.env.ref(".".join([xmlid_module, 'stage_optional']))
                self.env.ref(".".join([xmlid_module, 'stage_done']))
            except ValueError:
                raise ValueError(_("Not all stages were found"))

            self.env["project.task"].create(
                {
                    "outplacement_id": outplacement_id,
                    "joint_planing_type": "preplaning",
                    "task_type": task.task_type,
                    "activity_id": task.id,
                    "name": task.name,
                    "color": task.color,
                    "planned_hours": task.planned_hours,
                    "stage_id": stage_optional.id if task.task_type == "optional" else stage_todo.id,
                    "sequence": task.sequence,
                    "instructions": task.instructions
                }
            )

    @api.model
    def init_joint_planning_stages(self, outplacement_id):
        for stage in self.env["project.task.type"].search(
                [("is_outplacement", "=", True)]
        ):
            stage.outplacement_ids = [(4, outplacement_id)]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages = super(ProjectTask, self)._read_group_stage_ids(stages, domain, order)
        if [elem for elem in domain if "outplacement_id" in elem]:
            return stages.search([("is_outplacement", "=", True)])
        return stages

    @api.constrains("stage_id")
    def constrain_stage_id(self):
        try:
            stage_todo = self.env.ref(".".join([xmlid_module, 'stage_todo']))
            stage_optional = self.env.ref(".".join([xmlid_module, 'stage_optional']))
        except ValueError:
            raise ValueError(_("Not all stages were found"))
        if self.task_type == "mandatory" and self.stage_id.id == stage_optional.id:
            self.stage_id = stage_todo.id
            raise ValidationError(
                _("%s is a required task and can not be made optional.")
                % self.name)
        elif self.task_type == "optional" and (self.stage_id.id == stage_todo.id and not self.child_ids):
            self.stage_id = stage_optional.id
            raise UserError(_("An optional task with no sub-tasks can't be made required"))
        elif self.task_type == "optional" and (self.stage_id.id == stage_todo.id and self.child_ids):
            for child in self.child_ids:
                if child.stage_id == stage_todo.id:
                    self.stage_id = stage_todo.id
                    raise UserError(_("An optional task with sub-tasks"
                                      "in To Do stage can't be made optional"
                                      "until the required sub-tasks are done"))
        elif not self.task_type and (self.stage_id.id == stage_todo.id or self.stage_id.id == stage_optional.id):
            self.stage_id = False
            raise ValidationError(_("You are not allowed to add new required or optional tasks."))

    @api.depends("stage_id")
    def move_children(self):
        try:
            stage_done = self.env.ref(".".join([xmlid_module, 'stage_done']))
        except ValueError:
            raise ValueError(_("Done stage not found"))
        if self.stage_id.id == stage_done.id:
            for child in self.child_ids:
                # close task here (how?)
                child.stage_id = stage_done.id

    @api.multi
    def unlink(self):
        for task in self:
            if task.task_type == "mandatory":
                raise UserError(_('You are not allowed to remove requred tasks'))
        return models.Model.unlink(self)

    @api.model
    def create(self, vals):
        try:
            stage_todo = self.env.ref(".".join([xmlid_module, 'stage_todo']))
            stage_optional = self.env.ref(".".join([xmlid_module, 'stage_optional']))
        except ValueError:
            raise ValueError(_("Not all stages were found"))
        if vals.get('parent_id'):
            parent = self.env['project.task'].browse(vals['parent_id'])
            if parent.task_type != "optional":
                vals['stage_id'] = stage_todo.id
            else:
                vals['stage_id'] = stage_optional.id
            vals['color'] = parent.color
            vals['task_type'] = parent.task_type
            vals['outplacement_id'] = parent.outplacement_id.id
            # with the current handling of sequence this only allows a total of 9 sub-tasks
            # before things start to act a bit weird.
            # If we need more then sequence should be changed in res_joint_planning_af/data/data.xml
            vals['sequence'] = parent.sequence + len(parent.child_ids)
        elif not vals.get("task_type"):
            vals['task_type'] = "optional"
            vals['stage_id'] = stage_optional.id
        task = super(ProjectTask, self).create(vals)
        return task


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    def _get_default_outplacement_ids(self):
        default_outplacement_id = self.env.context.get("default_outplacement_id")
        if default_outplacement_id:
            return [(4, self.env.context.get("default_outplacement_id"), 0)]
        # default_outplacement_id = self.env.context.get("default_outplacement_id")
        # return [default_outplacement_id] if default_outplacement_id else None
        # fields.Many2many(comodel_name="_", string="_")  # relation|column1|column2

    outplacement_ids = fields.Many2many(
        comodel_name="outplacement",
        relation="outplacement_task_type_rel",
        column1="type_id",
        column2="outplacement_id",
        string="Outplacement",
        default=_get_default_outplacement_ids,
    )
    is_outplacement = fields.Boolean(string="Is Outplacement")

    @api.multi
    def unlink(self):
        stages = self
        default_outplacement_id = self.env.context.get("default_outplacement_id")
        if default_outplacement_id:
            shared_stages = self.filtered(
                lambda x: len(x.outplacement_ids) > 1 and default_outplacement_id in x.outplacement_ids.ids
            )
            tasks = (
                self.env["project.task"]
                    .with_context(active_test=False)
                    .search(
                    [
                        ("outplacement_id", "=", default_outplacement_id),
                        ("stage_id", "in", self.ids),
                    ]
                )
            )
            if shared_stages and not tasks:
                shared_stages.write(
                    {"outplacement_ids": [(3, default_outplacement_id)]}
                )
                stages = self.filtered(lambda x: x not in shared_stages)
        return super(ProjectTaskType, stages).unlink()
