# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models, modules, fields


_logger = logging.getLogger(__name__)


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    @api.model
    def systray_get_booking_activities(self):
        query = """SELECT m.id, count(*), act.res_model as model,
                            CASE
                                WHEN act.active = TRUE THEN 'active_booking'
                                WHEN act.active = FALSE THEN 'done_booking'
                                WHEN act.active = TRUE AND act._interpreter_booking_status = '1' 
                                   AND act._interpreter_booking_status_2  = '2' THEN 'failed_booking'
                                WHEN act.active = TRUE AND act._interpreter_booking_status = '1' 
                                   AND act._interpreter_booking_status_2 = ANY (ARRAY['1', '3']) THEN 'awaiting_booking'

                            END AS states
                        FROM mail_activity AS act
                        JOIN ir_model AS m ON act.res_model_id = m.id
                        WHERE user_id = %(user_id)s
                        GROUP BY m.id, states, act.res_model;
                        """
        self.env.cr.execute(query, {
            'today': fields.Date.context_today(self),
            'user_id': self.env.uid,
        })
        activity_data = self.env.cr.dictfetchall()
        model_ids = [a['id'] for a in activity_data]
        model_names = {n[0]: n[1] for n in self.env['ir.model'].browse(model_ids).name_get()}

        user_activities = {}
        for activity in activity_data:
            if not user_activities.get(activity['model']):
                user_activities[activity['model']] = {
                    'name': model_names[activity['id']],
                    'model': activity['model'],
                    'type': 'activity',
                    'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
                    'total_count': 0,
                    'active_booking_count': 0,
                    'done_booking_count': 0,
                    'failed_booking_count': 0,
                    'awaiting_booking_count': 0,
                }
            if activity.get('states'):
                user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
                user_activities[activity['model']]['total_count'] += activity['count']

        return list(user_activities.values())
