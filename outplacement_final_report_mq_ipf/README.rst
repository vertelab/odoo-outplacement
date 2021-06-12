==================================================
Outplacement final report MQ/IPF-update dispatcher
==================================================

To set up set system parameters:
outplacement_final_report_mq_ipf.mqhostport - ipfmq<1-3>-<environment>.arbetsformedlingen.se:61613

outplacement_final_report_mq_ipf.mquser - dafa

outplacement_final_report_mq_ipf.mqpwd

optional:

outplacement_final_report_mq_ipf.mqusessl - set to 0 if testing with activemq

outplacement_final_report_mq_ipf.stomp_logger - DEBUG if debugging is needed

outplacement_final_report_mq_ipf.cronstop - set to 0 as normal, 1 to disable


The module is maintained here: https://github.com/vertelab/odoo-outplacement/tree/Dev-12.0-Fenix-Sprint-02/outplacement_final_report_mq_ipf

Different version submitted
===========================

1. v12.0.0.1.1 - Fixed cron data.
2. v12.0.0.1.2 - Refactored code and bugfixes and better rejection message.
3. v12.0.0.1.3 - fixed datetime date mismatch.
4. v12.0.0.1.4 - fixed datetime date mismatch.

Maintainers
~~~~~~~~~~~

This module is maintained by Vertal.