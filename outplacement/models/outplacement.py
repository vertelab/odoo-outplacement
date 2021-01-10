import base64

from datetime import timedelta
from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource


import logging
_logger = logging.getLogger(__name__)


class Outplacement(models.Model):
    _name = 'outplacement'
    _description = 'Outplacement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'outplacement', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(
            base64.b64encode(open(image_path, 'rb').read()))

    def _default_stage_id(self):
        return self.env['outplacement.stage'].search(
            [('fold', '=', False)], limit=1)

    name = fields.Char(string="Name")
    stage_id = fields.Many2one(comodel_name='outplacement.stage',
                               string="State",
                               ondelete='restrict',
                               track_visibility='onchange',
                               index=True, copy=False,
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._default_stage_id()
                               )
    
    @api.model
    def _read_group_employee_ids(self, employees, domain, order):
        """ Always display all stages """
        _logger.warn('group by employee domain %s order %s' % (domain, order))
        if ['my_department', '=', True] in domain:
            department = self.env['hr.employee'].search(
                [('user_id', '=', self.env.user.id)], limit=1).mapped('department_id') or None
            domain=['|', ('department_id', '=', department.id if department else None), ('department_id', '=', None)]
        else:
            domain=[]
        _logger.warn('group by employee domain %s order %s' % (domain,order))
        return employees.search(domain, order=order)
    employee_id = fields.Many2one('hr.employee', string="Coach", group_expand='_read_group_employee_ids')
    department_id = fields.Many2one('hr.department',
                                    related="employee_id.department_id",
                                    group_expand='_read_group_department_ids',
                                    store=True)
    color = fields.Integer('Kanban Color Index')
    meeting_remote = fields.Selection(selection=[('no','On Premice'),('yes','Remote')],string='Meeting type')
    uniq_ref = fields.Char(string='Uniq Id', size=64, trim=True, )

    status = fields.Selection(string="status", selection=[
        ('10', 'Approved'), 
        ('20', 'Not approved'), 
        ('30', 'In-Progress'), 
        ('40', 'Rejected'), 
        ('50', 'Cancelled'), 
        ('60', 'Sent')
        ])
    late = fields.Boolean(string="Sent late")
    interruption = fields.Boolean(string="Interrupted")
    incomplete = fields.Boolean(string="Incomplete")

    # TODO!
    # Nils: Remove Image as we have no image of the jobseeker?
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char(related='partner_id.name', string='Partner Name', readonly=False)
    partner_street = fields.Char(related="partner_id.street", readonly=False)
    partner_street2 = fields.Char(related="partner_id.street2", readonly=False)
    partner_zip = fields.Char(related="partner_id.zip", readonly=False)
    partner_city = fields.Char(related="partner_id.city", readonly=False)
    partner_state_id = fields.Many2one(related="partner_id.state_id", readonly=False)
    country_id = fields.Many2one(related="partner_id.country_id", readonly=False) #because of a strange bug with partner_state_id this field must have this name
    partner_phone = fields.Char(string="Phone", related="partner_id.phone", readonly=False)
    partner_email = fields.Char(string="Email", related="partner_id.email", readonly=False)
    booking_ref = fields.Char()
    service_start_date = fields.Date()
    service_end_date = fields.Date()
    my_department = fields.Boolean(compute='_compute_my_department',
                                   search='_search_my_department')
    my_outplacement = fields.Boolean(compute='_compute_my_outplacement',
                                     search='_search_my_outplacement')
    sprakstod = fields.Char()

    # Nils: If image is removed this should be removed as well.
    @api.onchange('employee_id')
    def _employee_image(self):
        if self.employee_id:
            self.image = self.employee_id.image

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Always display all stages """
        return stages.search([], order=order)

    @api.model
    def _read_group_department_ids(self, departments, domain, order):
        """ Always display all stages """
        _logger.warn('group by department domain %s order %s' % (domain,order))
        return departments.search([], order=order)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if not vals.get('uniq_ref'):
            vals['uniq_ref'] = self.env['ir.sequence'].get(
                'outplacement.uniqid')
        return super(Outplacement, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(Outplacement, self).write(vals)
        return res

    @api.multi
    def _compute_my_department(self):
        department = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)]).mapped('department_id')
        department = department[0] if len(department) > 0 else None
        return self.filtered(lambda o: o.department_id == department)

    def _search_my_department(self, operator, value):
        user_employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)
        res = []
        if user_employee and user_employee.department_id:
            res = self.search([
                ('department_id', '=', user_employee.department_id.id)]).ids
        return [('id', operator, res)]

    def _compute_my_outplacement(self):
        coach = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        coach = coach[0] if len(coach) > 0 else None        
        return self.filtered(lambda o: o.employee_id == coach)

    def _search_my_outplacement(self, operator, value):
        user_employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)
        res = []
        if user_employee and user_employee.department_id:
            res = self.search([
                ('employee_id', '=', user_employee.id)]).ids
        return [('id', operator, res)]

    @api.multi
    def _track_template(self, tracking):
        res = super(Outplacement, self)._track_template(tracking)
        doc = self[0]
        changes, dummy = tracking[doc.id]
        if 'stage_id' in changes and doc.stage_id.template_id:
            res['stage_id'] = (doc.stage_id.template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'notif_layout': 'mail.mail_notification_light'
            })
        return res

    @api.multi
    def _notify_get_reply_to(self, default=None, records=None, company=None, doc_names=None):
        """ Override to set alias of Outplacements to their job definition if any. """
        aliases = self.mapped('job_id')._notify_get_reply_to(default=default, records=None, company=company, doc_names=None)
        res = {app.id: aliases.get(app.job_id.id) for app in self}
        leftover = self.filtered(lambda rec: not rec.job_id)
        if leftover:
            res.update(super(Outplacement, leftover)._notify_get_reply_to(default=default, records=None, company=company, doc_names=doc_names))
        return res

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(Outplacement, self).message_get_suggested_recipients()
        for Outplacement in self:
            if Outplacement.partner_id:
                Outplacement._message_add_suggested_recipient(recipients, partner=Outplacement.partner_id, reason=_('Contact'))
            elif Outplacement.email_from:
                Outplacement._message_add_suggested_recipient(recipients, email=Outplacement.email_from, reason=_('Contact Email'))
        return recipients

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        self = self.with_context(default_user_id=False)
        val = msg.get('from').split('<')[0]
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'partner_name': val,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        if custom_values:
            defaults.update(custom_values)
        return super(Outplacement, self).message_new(msg, custom_values=defaults)

    def _message_post_after_hook(self, message, *args, **kwargs):
        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(Outplacement, self)._message_post_after_hook(message, *args, **kwargs)

    @api.model
    def create_activities(self, record):
        product = record.order_id.order_line.mapped('product_id').filtered(lambda p: p.is_suborder)
        if product:
            for activity in product.mail_activity_ids:
                self.env['mail.activity'].create({
                        'res_id': record.id,
                        'res_model': record._name,
                        'res_model_id': self.env['ir.model'].search([('model', '=', record._name)]).id,
                        'activity_type_id': activity.activity_type_id.id,
                        'date_deadline': fields.Date.today() + timedelta(days=activity.due_days),
                        'summary': activity.summary,
                        'user_id': record.employee_id.user_id.id,
                })


class OutplacementStage(models.Model):
    _name = 'outplacement.stage'
    _description = 'Outplacement Stage'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    fold = fields.Boolean(string="Fold")
    template_id = fields.Many2one('mail.template', string="Mail Template")
