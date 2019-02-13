# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NeonetyCountry(models.Model):
	_name = 'res.country'
	_inherit = 'res.country'
	province_ids = fields.One2many(
	    'neonety.province',
	    'country_id',
	    string='Provincias',
	    ondelete='cascade'
	)


class NeonetyProvince(models.Model):
	_name = 'neonety.province'
	code = fields.Char(
		string='Código',
		size=3,
		required=True,
		translate=True)
	name = fields.Char(
		string='Nombre',
		size=255,
		required=True,
		translate=True)
	country_id = fields.Many2one(
	    'res.country',
	    string='País',
	    required=False,
	    translate=True,
	    compute='_get_country_id',
	    store=True,
	    ondelete='cascade')
	district_ids = fields.One2many(
	    'neonety.district',
	    'province_id',
	    string='Distritos'
	)

	@api.depends('name')
	def _get_country_id(self):
		country = self.pool.get('res.country')
		country_id = self.env['res.country'].search([['name', '=', 'Panama']]).id
		self.country_id = country_id


class NeonetyDistrict(models.Model):
	_name = 'neonety.district'
	code = fields.Char(
		string='Código',
		size=3,
		required=True,
		translate=True)
	name = fields.Char(
		string='Nombre',
		size=255,
		required=True,
		translate=True)
	country_id = fields.Many2one(
	    'res.country',
	    string='País',
	    required=False,
	    translate=True,
	    compute='_get_country_id',
	    store=True)
	province_id = fields.Many2one(
	    'neonety.province',
	    string='Distrito',
	    required=False,
	    translate=True)
	sector_ids = fields.One2many(
	    'neonety.sector',
	    'district_id',
	    string='Corregimientos',
	)

	@api.depends('name')
	def _get_country_id(self):
		country = self.pool.get('res.country')
		country_id = self.env['res.country'].search([['name', '=', 'Panama']]).id
		self.country_id = country_id


class NeonetySector(models.Model):
	_name = 'neonety.sector'
	code = fields.Char(
		string='Código',
		size=3,
		required=True,
		translate=True)
	name = fields.Char(
		string='Nombre',
		size=255,
		required=True,
		translate=True)
	country_id = fields.Many2one(
	    'res.country',
	    string='País',
	    required=False,
	    translate=True,
	    compute='_get_country_id',
	    store=True)
	province_id = fields.Many2one(
	    'neonety.province',
	    string='Distrito',
	    required=False,
	    translate=True)
	district_id = fields.Many2one(
	    'neonety.district',
	    string='Distrito',
	    required=False,
	    translate=True)

	@api.depends('name')
	def _get_country_id(self):
		country = self.pool.get('res.country')
		country_id = self.env['res.country'].search([['name', '=', 'Panama']]).id
		self.country_id = country_id

class NeonetyPartnerConcept(models.Model):
	_name = 'neonety.partner.concept'
	name = fields.Char(
	    string='Concepto',
	    required=True,
	    translate=True)
	status = fields.Boolean(
	    string='Estatus',
	    required=True,
	    translate=True)


class NeonetyPartner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'
	ruc = fields.Char(
	    string='RUC',
	    size=20,
	    required=False,
	    translate=True)
	dv = fields.Char(
	    string='DV',
	    size=2,
	    required=False,
	    translate=True)
	operation_notice_number = fields.Char(
	    string=' No. Aviso de Operación',
	    size=50,
	    required=False,
	    translate=True)
	partner_nationality = fields.Selection([
		('local', 'Local'),
		('extranjero', 'Extranjero')],
		string='Nacionalidad del cliente ó proveedor',
		required=False, translate=True)
	partner_type = fields.Selection([
		('natural', 'Persona natural (N)'),
		('juridica', 'Persona jurídica (J)'),
		('extranjero', 'Extranjero (E)')],
		string='Tipo de cliente ó proveedor',
		required=False, translate=True)
	neonety_partner_concept_id = fields.Many2one(
	    'neonety.partner.concept',
	    string='Concepto',
	    required=False,
	    translate=True)
	neonety_country_id = fields.Many2one(
	    'res.country',
	    string='País',
	    required=False,
	    translate=True,
	    default=174)
	country_id = fields.Many2one(
	    'res.country',
	    string='País',
	    required=False,
	    translate=True,
	    default=174)
	province_id = fields.Many2one(
	    'neonety.province',
	    string='Distrito',
	    required=False,
	    translate=True)
	district_id = fields.Many2one(
	    'neonety.district',
	    string='Distrito',
	    required=False,
	    translate=True)
	sector_id = fields.Many2one(
	    'neonety.sector',
	    string='Corregimiento',
	    required=False,
	    translate=True)
	street = fields.Char(
	    string='Dirección',
	    required=False,
	    translate=True)

	@api.onchange('neonety_country_id')
	def onchange_neonety_country_id(self):
		res = {}

		if self.neonety_country_id:
			self._cr.execute('SELECT id, name FROM neonety_province WHERE country_id = %s', (self.neonety_country_id.id, ))
			provinces = self._cr.fetchall()
			ids = []

			for province in provinces:
				ids.append(province[0])
			res['domain'] = {'province_id': [('id', 'in', ids)]}
		return res

	@api.onchange('province_id')
	def onchange_province_id(self):
		res = {}

		if self.province_id:
			self._cr.execute('SELECT neonety_district.id, neonety_district.name FROM neonety_district WHERE neonety_district.province_id = %s AND neonety_district.country_id = ( SELECT neonety_province.country_id FROM neonety_province WHERE neonety_province.id = %s) ', (self.province_id.id, self.province_id.id))
			districts = self._cr.fetchall()
			ids = []

			for district in districts:
				ids.append(district[0])
			print ids
			res['domain'] = {'district_id': [('id', 'in', ids)]}
		return res

	@api.onchange('district_id')
	def onchange_district_id(self):
		res = {}

		if self.district_id:
			self._cr.execute('SELECT neonety_sector.id, neonety_sector.name FROM neonety_sector WHERE neonety_sector.district_id = %s AND  neonety_sector.country_id = ( SELECT neonety_district.country_id FROM neonety_district WHERE neonety_district.id = %s) ', (self.district_id.id, self.district_id.id))
			sectors = self._cr.fetchall()
			ids = []

			for sector in sectors:
				ids.append(sector[0])
			res['domain'] = {'sector_id': [('id', 'in', ids)]}
		return res