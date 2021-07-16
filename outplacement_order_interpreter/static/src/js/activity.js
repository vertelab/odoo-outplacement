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

            let dialog = new Dialog(this, {'title': 'Avboka tolkbokningen',
                                           '$content': $('<p>
                                                         <b>Avboka tolkbokningen</b> <br>
                                                         Avbokning sker i tre steg: <br/>
                                                         1 Informera tolken om att ni inte kan använda tiden.<br/>
                                                         Tolkens namn : &nbsp'+activity.interpreter_name+'<br/>
                                                         Tolkens telefonnummer: &nbsp'+activity.interpreter_phone+'<br/>
                                                         2 Skicka ett epostmeddelande till&nbsp<a href="mailto:team-crm@arbetsformedlingen.se?subject=Avboka tolk med referens ' + activity.interpreter_booking_ref + ' och KA-Nr: ' + activity.interpreter_ka_nr + '."> team-crm@arbetsformedlingen.se</a> &nbsp och ange referensnummer&nbsp'+ activity.interpreter_booking_ref +'.<br/>
                                                         Aktuellt KA-Nr:&nbsp'+activity.interpreter_ka_nr+'.<br/>
                                                         3 Klicka på inleverera tolken.<br/>
                                                         </p>'),
                                           'technical':'false',
                                           'buttons':[
                                               {'text':'Inleverera tolken', 'close':'true', 'classes':'btn-primary',
                                               'click':function(){self.interpreter_deliver(options, activity)}},
                                               {'text':'Stäng', 'close':'true'}]})
            dialog.open()
            return
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
});

});