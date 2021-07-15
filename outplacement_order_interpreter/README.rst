Outplacement Order Interpreter
==============================
This module adds interpreter-functionality.

Different version submitted
===========================
1. v12.0.0.2 changed the languagecodes from a full list to Tolkportalens list. AFC-1586
2. v12.0.1.0.3 Added Category Outplacement
3. v12.0.1.0.3 Added fields to Outplacement view
4. v12.0.1.0.5 Hardening of interpreter-booking-parsing
5. v12.0.1.1.0 Made some fields obligatory.
6. v12.0.1.2.0 Added field adressat, removed edit and create from some fields.
7. v12.0.1.3.0 Changes to validation rules.
8. v12.0.1.4.0 Hide date due for interpreter bookings
9. v12.0.1.4.1 Bugfix of cronjob, Handling of removal of parent task.
10. v12.0.1.4.2 Added sequence to interpreter-booking-view.
11. v12.0.1.5.0 Archive instead of removing.
12. v12.0.1.5.1 Fixed crash at delivery.
13. v12.0.1.5.2 Fixed wrong status message on cancelation.
14. v12.0.1.5.3 Changed cancellation instruction message.
15. v12.0.1.5.4 Fixed typo in cancelling message.
16. v12.0.1.5.5 AFC-2028: Making fields readonly/not able to create on the fly.
17. v12.0.1.5.6 AFC-2145: Various text formating fixes, translations
18. V12.0.1.6.0 AFC-2125: This version adds a widget for displaying interpreter-bookings.
19. V12.0.1.6.1 AFC-2125: This version updates a widget for displaying interpreter-bookings with activity views and new filters.
20. V12.0.1.6.2 AFC-2217: This version adds new menu 'Interpreters' for 'Interpreter Accountants'.
21. V12.0.1.6.3 AFC-2145: This version updates Interpreter booking Log messages.
22. V12.0.1.6.4 AFC-2145: This version adds email to case worker on Interpreter bookings.
23. V12.0.1.6.5 AFC-2217: Added fixes for duplicate status messages in the chatter-log.
24. V12.0.1.6.6 AFC-2125: Hide project code field in popup of Delivered button inside activity.
25. V12.0.1.6.7 AFC-2363: Hide activity done log, Added server action to remove repetative booking confirmed log, Updated translation, Hide 'Inleverera tolk' button after delivered booking.
26. V12.0.1.6.8 AFC-2363: Enabled activity.js file to show popup when cancelling activity.
27. v12.0.1.6.9 AFC-2405: Improved Transaltion, Added 'Booking' smart button inside Outplacement, Added README.rst file,
    Hide 'Deliver Interpreter' button for 'Not Available Interpreter' Bookings, For now Hide cancel booking functionality.
28. v12.0.1.7.0 AFC-2405: Added different serach view for Interpreter bookings.
29. v12.0.1.7.1 AFC-2406: Redesign of the interpreter accountant formview.
30. v12.0.1.7.2 AFC-2441 AFC-2445: Added groupby Booking status, Added Calender & Pivot view for Interpreter Booking,
    Added new filter 'Cancelled By Interpreter' in Interpreter tray widget.
31. v12.0.1.7.3 AFC-2505 Added Jobseeker category in Interpreter booking.
32. v12.0.1.7.4 AFC-2358 Added server action and updated code to update duration of booking in two decimal, Added text 'Please submit Interpreter' on kanban if booking is not delivered, Added breadcrumbs for activity.
33. v12.0.1.7.5 AFC-2568 Made 'Interpreter Gender Preference' editable.
34. v12.0.1.7.6 AFC-2581 Added dynamic date filter to outplacement interpreter booking filter view.
35. v12.0.1.7.7 Added info about informing the interpreter when the interpreter is cancelled in activity.js-file
36. v12.0.1.7.8 AFC-2596 Listed all activities from Interpreters menus.
30. v12.0.1.7.9 AFC-2601: Trivial spelling corrections, line length and other trivial improvements

Maintainers
~~~~~~~~~~~

This module is maintained by Vertel AB <www.vertel.se> on behalf of Arbetsförmedlingen <www.arbetsformedlingen.se>

This module is maintained from: https://github.com/vertelab/odoo-outplacement/tree/Dev-12.0-Fenix-Sprint-02/outplacement_order_interpreter

Contributors
~~~~~~~~~~~~
* Anders Wallenquist <anders.wallenquist@vertel.se>
* Anil Kesariya <anil.r.kesariya@gmail.com>
* Fredrik Arvas <fredrik.arvas@vertel.se>
* Rupareliya Hemangi <rupareliyahemangi145@gmail.com>
* Nils Nyman-Waara <nils.nyman-waara@vertel.se>
