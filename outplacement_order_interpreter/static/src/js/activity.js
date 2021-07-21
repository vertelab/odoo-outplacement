odoo.define('mail.Activity.Interpreter', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;
var Dialog = require('web.Dialog')

var MailActivity = require('mail.Activity')

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
        var activityID = $(ev.currentTarget).data('activity-id');
        options = _.defaults(options || {}, {
            model: 'mail.activity',
            args: [[activityID]],
        });
        var activity = _.filter(this.record.specialData.activity_ids, function(activity){return activity.id == activityID})[0];
        var self = this;
        if (activity.is_interpreter_order) {
            // If we are trying to remove an interpreter booking ask the user
            // if all things the user have to do before removing it has been done.
            var content = '<p><b>Avboka tolkbokningen</b> <br> Avbokning sker i steg: <br/>'
            if (activity.interpreter_name) {
                content +=  '- Informera tolken om att ni inte kan använda tiden.<br/>' + "Tolkens namn : " + activity.interpreter_name + "<br/>"
            }
            if (activity.interpreter_phone) {
                content += "Tolkens telefonnummer: " + activity.interpreter_phone + "<br/>"
            }
            content += "- Skicka ett epostmeddelande till "
            var link = "mailto:team-crm@arbetsformedlingen.se?subject=Avboka tolk med referens " + activity.interpreter_booking_ref + " och KA-Nr: " + activity.interpreter_ka_nr + "."
            content += "<a href=\" " + link + " \">team-crm@arbetsformedlingen.se</a>"
            content += " och ange referensnummer "
            content += activity.interpreter_booking_ref + ".<br/> Aktuellt KA-Nr: " + activity.interpreter_ka_nr
            content += ".<br/> - Klicka på inleverera tolken.<br/></p>"
            if (activity._interpreter_booking_status_2 == '2') {
                let dialog = new Dialog(this, {'title': 'Avboka tolkbokningen',
                                           '$content': $('<div>', {
                                                html: content,
                                            }),
                                           'buttons': [{'text':'Markera som Avbokad', 'close':'true',
                                               'click':function(){self.interpreter_cancel(options)}}]})
                dialog.open()
                return
            }
            else {
                let dialog = new Dialog(this, {'title': 'Avboka tolkbokningen',
                                           '$content': $('<div>', {
                                                html: content,
                                            }),
                                           'buttons':[
                                               {'text':'Inleverera tolken', 'close':'true', 'classes':'btn-primary',
                                               'click':function(){self.interpreter_deliver(options, activity)}},
                                               {'text':'Markera som Avbokad', 'close':'true',
                                               'click':function(){self.interpreter_cancel(options)}}]})
                dialog.open()
                return
            }
        };
        return this._rpc({
                model: options.model,
                method: 'unlink',
                args: options.args,
            })
            .then(this._reload.bind(this, {activity: true}));
    },
    interpreter_deliver: function (options, activity){
        // Unlink, logg, reload.
        var action = {
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
        var callback = this._reload.bind(this, { activity: true, thread: true });
        return this.do_action(action, { on_close: callback });
    },
    interpreter_cancel: function (options){
        // Unlink, logg, reload.
        this._rpc({model: options.model, method: 'interpreter_cancel_booking', args: options.args})
        .then(this._reload.bind(this, {activity: true}));
    },
});

});
