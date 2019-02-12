# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import date
import logging
_logger = logging.getLogger(__name__)


class SaleOrderToCancelReport(models.Model):
    _name = 'ancon.sale.order.to.cancel.report'
    _auto = False
    _order = 'id'
    id = fields.Integer(
        string='ID',
        readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'ancon_sale_order_to_cancel_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW ancon_sale_order_to_cancel_report AS
            SELECT
                sale_order.id AS id
            FROM
                sale_order
                INNER JOIN account_payment_term
                    on account_payment_term.id = sale_order.payment_term_id
                        AND account_payment_term.payment_term_type LIKE 'credit_payment'
            WHERE
                sale_order.state LIKE 'sale'
                AND sale_order.invoice_status LIKE 'to invoice'
                AND sale_order.canceled_at = '{0}'
            ORDER BY
                sale_order.id
                        """.format(date.today().strftime('%Y-%m-%d')))

    @api.multi
    def cancel_sale_order(self):
        """
        Automatic task settings:
        Select the model "ancon.sale.order.to.cancel.report"
        type to task select "execute python code"
        on the textarea to add python code add: "model.cancel_sale_order()"
        """
        for sale_order in self.env['ancon.sale.order.to.cancel.report'].search_read([], {'fields': ['id']}):
            sale_order_id = sale_order['id']
            if sale_order_id and sale_order_id > 0:
                order = self.env['sale.order'].browse(sale_order_id)
                if order:
                    order.action_cancel()
