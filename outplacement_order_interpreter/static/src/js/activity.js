odoo.define('mail.Activity.Interpreter', function (require) {
    "use strict";

    let core = require('web.core');
    let _t = core._t;
    let Dialog = require('web.Dialog')

    let MailActivity = require('mail.Activity')

// -----------------------------------------------------------------------------
// Activities Widget for Form views ('mail_activity' widget)
// -----------------------------------------------------------------------------
    var Activity = MailActivity.include({

        /**
         * @private
         * @param {MouseEvent} ev
         * @param {Object} options
         * @returns {$.Promise}
         */
        _onUnlinkActivity: function (ev, options) {
            ev.preventDefault();
            let activityID = $(ev.currentTarget).data('activity-id');
            options = _.defaults(options || {}, {
                model: 'mail.activity',
                args: [[activityID]],
            });
            var activity = _.filter(this.record.specialData.activity_ids, function (activity) {
                return activity.id == activityID
            })[0];
            var self = this;
            if (activity.is_interpreter_order) {
                // We have not got any interpreter yet so its OK to cancel directly.
                console.log(activity._interpreter_booking_status_2)
                if (activity._interpreter_booking_status_2 == '2' || activity._interpreter_booking_status_2 == '1' || activity._interpreter_booking_status_2 == '3') {
                    self.interpreter_cancel(options)
                    return
                }
                let content = ''
                if (activity.interpreter_name || activity.interpreter_phone) {
                    content += '<p><b>Avboka tolkbokningen</b></br>'
                    content += '- Informera tolken om att ni inte kan använda tiden.<br/>'
                    if (activity.interpreter_name) {
                        content += "Tolkens namn : " + activity.interpreter_name + "<br/>"
                    }
                    if (activity.interpreter_phone) {
                        content += "Tolkens telefonnummer: " + activity.interpreter_phone + "<br/>"
                    }
                    let dialog = new Dialog(this, {
                        'title': 'Avboka tolkbokningen',
                        '$content': $('<div>', {
                            html: content,
                        }),
                        'buttons': [{
                            'text': 'Markera som Avbokad', 'close': 'true',
                            'click': function () {
                                // Deliver interpreter and then Cancel in Tolkportalen
                                let callback = self.interpreter_cancel(options)
                                self.interpreter_deliver(options, activity, callback)
                            }
                        }]
                    })
                        dialog.open()
                        return
                }
                // Deliver interpreter and then Cancel in Tolkportalen
                let callback = self.interpreter_cancel(options)
                self.interpreter_deliver(options, activity, callback)
                return
            }
            return this._rpc({
                model: options.model,
                method: 'unlink',
                args: options.args,})
                .then(this._reload.bind(this, {activity: true}));
        },

        interpreter_cancel: function (options){
            // Cancel booking in Tolkportalen and reload page.
            this._rpc({model: options.model, method: 'interpreter_cancel_booking', args: options.args})
                .then(this._reload.bind(this, {activity: true}));
        },
        interpreter_deliver: function (options, activity, callback){
            // Deliver interpreter and then call cancel.
            let action = {
                type: 'ir.actions.act_window',
                res_model: 'outplacement.interpreter_delivery.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    default_res_id: activity.id,
                    default_res_model: options.model,
                    active_id: activity.id,
                    early_ok: true
                },
            };
            return this.do_action(action, { on_close: callback });
        },
    });
});
