# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    canceled_at = fields.Date(
        string='Cancelado en',
        required=False,
        default=None)
    notified_at = fields.Date(
        string='Notificar en',
        required=False,
        default=None)
    first_payment_date = fields.Date(
        string='Fecha del primer abono',
        required=False,
        default=None)
    state = state = fields.Selection([
        ('draft', 'Quotation'),
        ('approved','Aprobado'),
        ('pending', 'Pendiente de Aprobación'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')])
    partner_ruc = fields.Char(
        string='RUC',
        related='partner_id.ruc',
        inverse='_inverse_ruc',
        compute='_get_ancon_parnter_info')

    def _get_ancon_parnter_info(self, partner):
        return {
            'partner_ruc': partner.ruc}

    def _inverse_ruc(self):
        for sale_order in self:
            sale_order.partner_id.ruc = sale_order.partner_ruc

    @api.model
    def create(self, vals):
        note = '' if not 'note' in vals else vals['note']
        if 'partner_id' in vals:
            partner_id = self.env['res.partner'].browse(vals['partner_id'])
            if partner_id:
                if hasattr(partner_id, 'sector_id'):
                    delivery_zones = self.env['ancon.delivery.zone'].search_read([
                        ('sector_ids', 'in', [partner_id.sector_id.id])], fields=['id', 'name', 'description'])
                    if len(delivery_zones) > 0:
                        delivery_info = "\n"
                        for dz in delivery_zones:
                            delivery_info += 'Ruta de entrega: {0}, información: {1}'.format(dz['name'], dz['description'])
                        note = '{0}{1}'.format(note, delivery_info)
        vals['note'] = note
        return super(SaleOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'first_payment_date' in vals:
            if vals['first_payment_date']:
                first_payment_date = vals['first_payment_date']
                date_obj = None
                if 'str' in first_payment_date.__class__.__name__:
                    date_obj = datetime.strptime(vals['first_payment_date'], '%Y-%m-%d')
                elif 'date' in first_payment_date.__class__.__name__:
                    date_obj = first_payment_date
                if date_obj:
                    vals['canceled_at'] = date_obj + timedelta(days=90)
                    vals['notified_at'] = date_obj + timedelta(days=80)
        return super(SaleOrder, self).write(vals)

    def _check_order_available_to_send(self, type):
        has_discount_products = 0
        counter = 0
        for line in self.order_line:
            if line.custom_discount > 0:
                counter += 1
        if counter > 0 and not 'approved' in self.state:
            raise ValidationError(
                "No es posible {0}, Necesita solicitar aprobación o eliminar el descuento.".format(type))

    @api.multi
    def action_confirm(self):
        self._check_order_available_to_send("Confirmar el presupuesto")
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_reject(self):
        self.action_cancel()
        self.action_draft()

    @api.multi
    def action_by_approve(self):
        return self.write({'state': 'pending'})

    @api.multi
    def action_approve(self):
        return self.write({'state': 'approved'})

    @api.multi
    def print_quotation(self):
        self._check_order_available_to_send("Imprimir")
        raise ValidationError("Error forzed")
        return super(SaleOrder, self).print_quotation()

    @api.multi
    def action_quotation_send(self):
        self._check_order_available_to_send("Enviar por correo")
        raise ValidationError("Error forzed")
        return super (SaleOrder, self).action_quotation_send()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    custom_discount = fields.Float(
        string='Descuento',
        default=0.00)

    @api.one
    @api.model
    def compute_custom_discount(self):
        price_subtotal = self.product_uom_qty * self.price_unit
        percentage = 0.00
        if price_subtotal > 0 and self.custom_discount > 0:
            percentage = (self.custom_discount/price_subtotal) * 100
        self.discount = percentage

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        order_line = super(SaleOrderLine, self)._compute_amount()
        for line in self:
            price_subtotal = line.product_uom_qty * line.price_unit
            percentage = 0.00
            if line.custom_discount > price_subtotal:
                raise ValidationError('El monto del descuento no puede ser mayor al subtotal')
            if price_subtotal > 0 and line.custom_discount > 0:
                percentage = (line.custom_discount/price_subtotal) * 100
            line.discount = percentage
            if line.price_unit < line.product_id.product_tmpl_id.list_price:
                raise ValidationError('El monto ${0:.2f} del producto {1} no puede ser menor de ${2:.2f}'.format(
                    line.price_unit, line.name, line.product_id.product_tmpl_id.list_price))
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'discount': line.discount,
                'custom_discount': line.custom_discount
            })

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['custom_discount'] = self.custom_discount
        return res
