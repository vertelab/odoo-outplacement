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
        query = """SELECT m.id, act.res_id, count(*), act.res_model as model,
                            CASE
                               WHEN act.active = ANY (ARRAY[TRUE, FALSE]) AND act._interpreter_booking_status_2 = '1' 
                                   Then 'order_received'

                               WHEN act.active = ANY (ARRAY[TRUE, FALSE]) AND act._interpreter_booking_status_2 = '2' 
                                   Then 'no_available_interpreter'
                                    
                               WHEN act.active = ANY (ARRAY[TRUE, FALSE]) AND act._interpreter_booking_status_2 = '3' 
                                   Then 'order_in_process'
                                   
                               WHEN act.active = ANY (ARRAY[TRUE, FALSE]) AND act._interpreter_booking_status_2 = '4' 
                                   Then 'interpreter_booked'
                                   
                               WHEN act.active = ANY (ARRAY[TRUE, FALSE]) AND act._interpreter_booking_status_2 = '5' 
                                   Then 'cancelled_by_interpreter'
                                   
                               WHEN act.active = ANY (ARRAY[TRUE, FALSE]) AND act._interpreter_booking_status_2 = '6' 
                                   Then 'cancelled_by_af'
                                   
                            END AS states
                        FROM mail_activity AS act
                        JOIN ir_model AS m ON act.res_model_id = m.id
                        WHERE user_id = %(user_id)s AND res_model = 'project.task'
                        GROUP BY m.id, states, act.res_model, act.res_id;
                        """
        self.env.cr.execute(query, {
            'today': fields.Date.context_today(self),
            'user_id': self.env.uid,
        })
        activity_data = self.env.cr.dictfetchall()
        new_activity_data = []
        task_obj = self.env['project.task']
        for activity_dict in activity_data:
            task_id = activity_dict.get('res_id')
            task = task_obj.browse(task_id)
            if task.outplacement_id:
                new_activity_data.append(activity_dict)
        model_ids = [a['id'] for a in new_activity_data]
        model_names = {n[0]: n[1] for n in self.env['ir.model'].browse(model_ids).name_get()}
        user_activities = {}
        for activity in new_activity_data:
            if not user_activities.get(activity['model']):
                user_activities[activity['model']] = {
                    'name': model_names[activity['id']],
                    'model': activity['model'],
                    'type': 'activity',
                    'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
                    'total_count': 0,
                    'order_received_count': 0,
                    'no_available_interpreter_count': 0,
                    'order_in_process_count': 0,
                    'interpreter_booked_count': 0,
                    'cancelled_by_af_count': 0,
                    'cancelled_by_interpreter_count': 0,
                }
            if activity.get('states'):
                user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
                user_activities[activity['model']]['total_count'] += activity['count']
        return list(user_activities.values())
