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
            let dialog = new Dialog(this, {'title': 'Cancel Interpreter',
                                           '$content': $('<p>
                                                         <b>Avboka tolkbokningen</b> <br>
                                                         Avboka tolken genom att skicka ett epostmeddelande till <a href="mailto:team-crm@arbetsformedlingen.se?subject=Avboka tolk med referens ' + activity.interpreter_booking_ref + '."> team-crm@arbetsformedlingen.se och ange referensnummer ' + activity.interpreter_booking_ref + '.
                                                         </p>'),
                                           'technical':'false',
                                           'buttons':[
                                               {'text':'Markera som Avbokad', 'close':'true', 'click':function(){self.interpreter_cancel(options)}},
                                               {'text':'Stäng rutan utan att markera som avbokad', 'close':'true', 'classes':'btn-primary'}]})
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
    interpreter_cancel: function (options){
        // Unlink, logg, reload.
        this._rpc({model: options.model, method: 'interpreter_cancel_booking', args: options.args})
        .then(this._reload.bind(this, {activity: true}));
    },
});

});
