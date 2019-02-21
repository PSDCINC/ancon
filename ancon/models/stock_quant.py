# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _name = 'stock.quant'
    _inherit = 'stock.quant'

    @api.multi
    def name_get(self):
        res = []
        for sq in self:
            res.append((sq.id, '{0} ({1})'.format(sq.location_id.company_id.name, round(sq.quantity))))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('location_id.company_id.name', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('location_id.company_id.name', operator, name)] + args, limit=limit)
        return recs.name_get()
