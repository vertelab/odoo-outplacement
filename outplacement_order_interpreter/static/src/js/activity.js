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
            let activity = _.filter(this.record.specialData.activity_ids, function (activity) {
                return activity.id == activityID
            })[0];
            let self = this;
            if (activity.is_interpreter_order) {
                // We have not got any interpreter yet so its OK to cancel directly.
                if (activity._interpreter_booking_status_2 == '2'){
                    self.interpreter_cancel(options)
                    return
                }
                let content = ''
                // Check if we are over the deadline and thus need to deliver the interpreter.
                if (activity.delivery_on_cancel()) {
                    // If we got information about the interpreter, tell user to contact interpreter as well.
                    if (activity.interpreter_name || activity.interpreter_phone){
                        content += '<p><b>Avboka tolkbokningen</b></br>'

                        if (activity.interpreter_name) {
                            content += '- Informera tolken om att ni inte kan använda tiden.<br/>' + "Tolkens namn : " + activity.interpreter_name + "<br/>"
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
                                    self.interpreter_deliver(options, activity)
                                }
                            }]
                        })
                        dialog.open()
                        return
                    }
                    // Deliver interpreter and then Cancel in Tolkportalen
                    self.interpreter_deliver(options, activity)
                    return
                }
                // If we are here then no delivery is needed, just do a cancel.
                self.interpreter_cancel(options)
                return
            };
            return this._rpc({
                model: options.model,
                method: 'unlink',
                args: options.args,})
                .then(this._reload.bind(this, {activity: true}));
        },

        interpreter_deliver: function (options, activity){
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
                    active_id: activity.id
                },
            };
            let callback = self.interpreter_cancel(options);
            return this.do_action(action, { on_close: callback });
        },
        interpreter_cancel: function (options){
            // Cancel booking in Tolkportalen and reload page.
            this._rpc({model: options.model, method: 'interpreter_cancel_booking', args: options.args})
                .then(this._reload.bind(this, {activity: true}));
        },
    });
});
