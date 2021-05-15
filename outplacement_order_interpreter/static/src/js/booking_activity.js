odoo.define('mail.Bookings.ActivityMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    /**
     * Menu item appended in the systray part of the navbar, redirects to the next
     * activities of all app
     */
    var BookingActivityMenu = Widget.extend({
        name: 'booking_activity_menu',
        template: 'Bookings.ActivityMenu',
        events: {
            'click .o_mail_activity_action': '_onActivityActionClick',
            'click .o_mail_preview': '_onActivityFilterClick',
            'show.bs.dropdown': '_onBookingActivityMenuShow',
        },

        willStart: function () {
            return $.when(this.call('mail_service', 'isReady'));
        },
        start: function () {
            this._$activitiesPreview = this.$('.o_mail_systray_dropdown_items');
            this.call('mail_service', 'getMailBus').on('activity_updated', this, this._updateCounter);
            this._updateCounter();
            this._updateBookingActivityPreview();
            return this._super();
        },
        //--------------------------------------------------
        // Private
        //--------------------------------------------------
        /**
         * Make RPC and get current user's activity details
         * @private
         */
        _getBookingActivityData: function () {
            var self = this;

            return self._rpc({
                model: 'res.users',
                method: 'systray_get_booking_activities',
                args: [],
                kwargs: {context: session.user_context},
            }).then(function (data) {
                self._activities = data;
                self.activityCounter = _.reduce(data, function (total_count, p_data) { return total_count + p_data.total_count || 0; }, 0);
                self.$('.o_notification_counter').text(self.activityCounter);
                self.$el.toggleClass('o_no_notification', !self.activityCounter);
            });
        },
        /**
         * Get particular model view to redirect on click of activity scheduled on that model.
         * @private
         * @param {string} model
         */
        _getActivityModelViewID: function (model) {
            return this._rpc({
                model: model,
                method: 'get_activity_view_id'
            });
        },
        /**
         * Update(render) activity system tray view on activity updation.
         * @private
         */

         _updateBookingActivityPreview: function () {
            var self = this;
            self._getBookingActivityData().then(function (){
                self._$activitiesPreview.html(QWeb.render('mail.systray.BookingActivityMenu.Previews', {
                    activities : self._activities
                }));
            });
        },

        /**
         * update counter based on activity status(created or Done)
         * @private
         * @param {Object} [data] key, value to decide activity created or deleted
         * @param {String} [data.type] notification type
         * @param {Boolean} [data.activity_deleted] when activity deleted
         * @param {Boolean} [data.activity_created] when activity created
         */
        _updateCounter: function (data) {
            if (data) {
                if (data.activity_created) {
                    this.activityCounter ++;
                }
                if (data.activity_deleted && this.activityCounter > 0) {
                    this.activityCounter --;
                }
                this.$('.o_notification_counter').text(this.activityCounter);
                this.$el.toggleClass('o_no_notification', !this.activityCounter);
            }
        },

        //------------------------------------------------------------
        // Handlers
        //------------------------------------------------------------

        /**
         * Redirect to specific action given its xml id
         * @private
         * @param {MouseEvent} ev
         */
        _onActivityActionClick: function (ev) {
            ev.stopPropagation();
            var actionXmlid = $(ev.currentTarget).data('action_xmlid');
            this.do_action(actionXmlid);
        },

        /**
         * Redirect to particular model view
         * @private
         * @param {MouseEvent} event
         */
        _onActivityFilterClick: function (event) {
            // fetch the data from the button otherwise fetch the ones from the parent (.o_mail_preview).
            var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
            var context = {};
            if (data.filter === 'my') {
                context['search_default_activities_all_booking'] = 1;
                context['search_default_activities_awaiting_booking'] = 1;
                context['search_default_activities_ongoing_booking'] = 1;
                context['search_default_activities_not_delivered_booking'] = 1;
                context['search_default_activities_failed_booking'] = 1;
                context['search_default_activities_done_booking'] = 1;
            } else {
                context['search_default_activities_' + data.filter] = 1;
            }
            if (data.filter === 'failed_booking') {
               context['search_default_activities_failed_booking'] = 1;
            }
            if (data.filter === 'done_booking') {
               context['search_default_activities_done_booking'] = 1;
            }
            if (data.filter === 'all_booking') {
               context['search_default_activities_all_booking'] = 1;
            }
            if (data.filter === 'ongoing_booking') {
               context['search_default_activities_ongoing_booking'] = 1;
            }
            if (data.filter === 'awaiting_booking') {
               context['search_default_activities_awaiting_booking'] = 1;
            }
            if (data.filter === 'not_delivered_booking') {
               context['search_default_activities_not_delivered_booking'] = 1;
            }
            this.do_action('outplacement_order_interpreter.interpreter_activity_action', {
               additional_context: context,
               clear_breadcrumbs: true,
            });
        },
        /**
         * @private
         */
        _onBookingActivityMenuShow: function () {
             this._updateBookingActivityPreview();
        },
    });

    var activityMenuIndex = _.findIndex(SystrayMenu.Items, function (SystrayMenuItem) {
        return SystrayMenuItem.prototype.name === 'activity_menu';
    });
    if (activityMenuIndex > 0) {
        console.log("activityMenuIndex", activityMenuIndex)
        SystrayMenu.Items.splice(activityMenuIndex, 0, BookingActivityMenu);
    } else {
        console.log("no way", activityMenuIndex)
        SystrayMenu.Items.push(BookingActivityMenu);
    }


    return BookingActivityMenu;

});
