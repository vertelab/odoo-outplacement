==============================
Outplacement Final Report send
==============================

This module adds a button to the outplacement interface that allows the sending of final reports.

The module is maintained here: https://github.com/vertelab/odoo-outplacement/tree/Dev-12.0-Fenix-Sprint-02/outplacement_final_report_send

Different version submitted
===========================

1. v12.0.0.1.1 Fixed views and made error messages more readable.
2. v12.0.0.1.2 Added warning stopping the user from sending too early.
3. v12.0.0.1.3 added chatter message.
4. v12.0.0.1.4 made it so that you can only send a day after service end.
5. v12.0.0.2.0 Added reset for final report rejection check.
6. v12.0.0.2.1 Added check to make sure joint planning is sent before sending final report.
7. v12.0.1.2.2 Fixed messages AFC-2174.
8. v12.0.1.2.3 Fixed messages AFC-2128.
9. v12.0.1.2.4 AFC-2560 Fixed better error message for IPF Config.
10. v12.0.1.2.5 AFC-2582 Adjusted calculation of allowed time to send Final Report.
11. v12.0.1.2.6 AFC-2600 Raised onscreen warnings for required fields when sending Final Report. Improved code for Final report Send date.
12. v12.0.1.2.7 AFC-2615 Raised onscreen warnings user send final report after service ended.
13. v12.0.1.2.8 AFC-2637 fixed always throwing UserError if outplacement was cancelled, empty main and alternative goals can now only be sent if you are within 15 days of order start
14. v12.0.1.2.9 AFC-2708 restored usererror on api error response.
14. v12.0.1.2.10 Moved amount of days to send final report to a system parameter.


Maintainers
~~~~~~~~~~~

This module is maintained by Vertel.
