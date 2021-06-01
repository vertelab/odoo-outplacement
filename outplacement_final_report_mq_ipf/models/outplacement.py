# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _, registry

import json
import logging
import stomp
import ssl
from queue import Queue, Empty
from time import time



_logger = logging.getLogger(__name__)


def subscribe(mqconn, target, clientid=4):
    mqconn.subscribe(destination=target, clientid=clientid, ack="client")


def connect_and_subscribe(mqconn, user, pwd, target, clientid=4):
    _logger.info(f"user: {user} pwd: {pwd}")
    mqconn.connect(user, pwd, wait=True)
    subscribe(mqconn, target, clientid=clientid)


JS_REF = "genomforandereferens_arbetssokande"
EMP_REF = "genomforandereferens_arbetsgivare"
ORDER_NR = "ordernummer"
MSGTYPE = "typ"
COMMENT = "kommentar"
TIMESTAMP = "tidpunkt"


class FinalReportListener(stomp.ConnectionListener):
    def __init__(self, mqconn, user, pwd, target, clientid=4):
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid
        self.__msgqueue = Queue()

    def __parse_message(self, message):
        msgdict = {}
        try:
            msgdict = json.loads(message)
        except:
            return None
        return msgdict

    def _handle_message(self, headers, message):
        data = self.__parse_message(message)
        _logger.debug("_handle_message: %s" % data)
        if data:
            # Add message to queue
            self.__msgqueue.put((headers, data))

    def next_message(self, block=False, timeout=5):
        """Fetch the next message in the queue."""
        try:
            return self.__msgqueue.get(block=block, timeout=timeout)
        except Empty:
            return

    def on_error(self, headers, body):
        """
        Called by the STOMP connection when an ERROR frame is received.

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload - usually a detailed error description.
        """
        _logger.error("Final report MQ Listener error: %s - %s" % (headers, body))

    def on_message(self, headers, msg):
        _logger.debug("Final report MQ Listener on_message: {0} - {1}".format(headers, msg))
        self._handle_message(headers, msg)

    def ack_message(self, msg):
        headers, body = msg
        # tell MQ we handled the message
        self.__conn.ack(headers["message-id"])

    def on_disconnected(self):
        # Probably happened because we asked to disconnect
        _logger.warning(
            "Final report MQ Listener disconnected from MQ - NOT Trying to reconnect"
        )

    def on_connecting(self, host_and_port):
        """
        Called by the STOMP connection once a TCP/IP connection to the
        STOMP server has been established or re-established. Note that
        at this point, no connection has been established on the STOMP
        protocol level. For this, you need to invoke the "connect"
        method on the connection.

        :param (str,int) host_and_port: a tuple containing the host name and port number to which the connection
            has been established.
        """
        _logger.debug("Final report MQ Listener on_conecting: {0}".format(host_and_port))

    def on_connected(self, headers, body):
        """
        Called by the STOMP connection when a CONNECTED frame is
        received (after a connection has been established or
        re-established).

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload. This is usually empty for CONNECTED frames.
        """
        _logger.debug("Final report MQ Listener on_connected: %s - %s" % (headers, body))


class Outplacement(models.Model):
    _inherit = "outplacement"

    def __get_host_port(self):
        str = self.env["ir.config_parameter"].get_param(
            "outplacement_final_report_mq_ipf.mqhostport", "ipfmq1-utv.arbetsformedlingen.se:61613"
        )
        hosts = list()
        for vals in str.split(","):
            hosts.append(tuple(vals.split(":")))

        return hosts

    @api.model
    def mq_fr_listener(self, minutes_to_live=10):
        _logger.info("Final report MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env["ir.config_parameter"].get_param(
            "outplacement_final_report_mq_ipf.target_final_report",
            "/queue/Consumer.dafa.VirtualTopic.arbetssokande.genomforandehandelse.event.created",
        )
        usr = self.env["ir.config_parameter"].get_param("outplacement_final_report_mq_ipf.mquser", "dafa")
        pwd = self.env["ir.config_parameter"].get_param(
            "outplacement_final_report_mq_ipf.mqpwd", "topsecret"
        )
        stomp_log_level = self.env["ir.config_parameter"].get_param(
            "outplacement_final_report_mq_ipf.stomp_logger", "INFO"
        )

        # decide the stomper log level depending on param
        stomp_logger = logging.getLogger("stomp.py")
        stomp_logger.setLevel(getattr(logging, stomp_log_level))

        mqconn = stomp.Connection10(host_port)

        if (
                self.env["ir.config_parameter"].get_param("outplacement_final_report_mq_ipf.mqusessl", "1")
                == "1"
        ):
            mqconn.set_ssl(for_hosts=host_port, ssl_version=ssl.PROTOCOL_TLS)
            _logger.debug("Final report MQ Listener - Using TLS")
        else:
            _logger.debug("Final report MQ Listener - Not using TLS")

        frlsnr = FinalReportListener(mqconn, usr, pwd, target, 4)
        mqconn.set_listener("", frlsnr)
        # passing a bool in do_list to indicate if we should keep
        # running mq_fr_sender. What is a better solution?
        try:
            connect_and_subscribe(mqconn, usr, pwd, target)

            limit = time() + minutes_to_live * 60

            while time() < limit:
                message = frlsnr.next_message()
                if message:
                    env_new = None
                    try:
                        new_cr = registry(self.env.cr.dbname).cursor()
                        uid, context = self.env.uid, self.env.context
                        with api.Environment.manage():
                            env_new = api.Environment(new_cr, uid, context)
                            _logger.debug("Final report MQ Sender: finding outplacement")
                            headers, msg = message
                            comment = msg.get(COMMENT)
                            employer = msg.get(EMP_REF)
                            order = msg.get(ORDER_NR)
                            jobseeker = msg.get(JS_REF)
                            # only relevant if it's a social security number
                            # jobseeker = f"{jobseeker[:8]}-{jobseeker[8:]}"
                            message_type = msg.get(MSGTYPE)
                            _logger.debug(f"Got message with order number {order}, "
                                          f"jobseeker reference {jobseeker}, "
                                          f"employer reference {employer}, "
                                          f"comment {comment}, "
                                          f"type {message_type}")
                            # not sure how specific the search has to be to find the right object
                            outplacement = env_new['outplacement'].search([# '&',
                                # ('partner_social_sec_nr', '=', jobseeker),
                                # ('some_field', '=', employer),
                                ('name', '=', order)])
                            if outplacement:
                                # possible values:
                                # Slutredovisning ej godkänd
                                # Slutredovisning inkommen
                                # Slutredovisning godkänd
                                if message_type == "Slutredovisning ej godkänd":
                                    outplacement.fr_rejected = True
                                    outplacement.message_post(body=message_type)
                                elif message_type == "Slutredovisning godkänd":
                                    outplacement.message_post(body=message_type)
                                frlsnr.ack_message(message)
                            else:
                                _logger.error(f"Failed to find outplacement with jobseeker ref {jobseeker} "
                                              f"and order number {order}")
                    except Exception as e:
                        _logger.exception(
                            f"Final report MQ Listener: error: {e}"
                        )
                    finally:
                        # close our new cursor
                        if env_new:
                            env_new.cr.close()
                self.env.cr.commit()
                # Check if stop has been called
                cronstop = self.env["ir.config_parameter"].get_param(
                    "outplacement_final_report_mq_ipf.cronstop", "0"
                )
                if cronstop != "0":
                    break
            # Stop listening
            mqconn.unsubscribe(target)
        except:
            _logger.exception("Something went wrong in MQ")
        finally:
            # send signal to stop other thread
            if mqconn.is_connected():
                mqconn.disconnect()
