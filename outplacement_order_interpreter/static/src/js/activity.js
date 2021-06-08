odoo.define('mail.Activity.Interpreter', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;


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
        // Activate when cancel operation is implemented.
        // if (activity.is_interpreter_order) {
        //     return this._rpc({
        //         model: options.model,
        //         method: 'interpreter_cancel_booking',
        //         args: options.args,
        //     })
        //     .then(this._reload.bind(this, {activity: true}));
        // };
        return this._rpc({
                model: options.model,
                method: 'unlink',
                args: options.args,
            })
            .then(this._reload.bind(this, {activity: true}));
    },
});

});
