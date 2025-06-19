# -*- coding: utf-8 -*-
################################################################################
#
#    Medical Care Analysis - Analyse des Produits Consommés
#
################################################################################
from odoo import api, fields, models, tools


class MedicalCareAnalysis(models.Model):
    """Analyse des produits consommés dans les soins médicaux"""
    _name = 'medical.care.analysis'
    _description = 'Analyse des Produits Consommés'
    _auto = False
    _rec_name = 'product_id'
    _order = 'date desc, product_id'

    # Champs de base
    date = fields.Date(string='Date', readonly=True)
    outpatient_id = fields.Many2one('hospital.outpatient', string='Visite', readonly=True)
    product_id = fields.Many2one('product.product', string='Produit', readonly=True)

    # Quantités
    quantity_used = fields.Float(string='Quantité Utilisée', readonly=True)
    quantity_billed = fields.Float(string='Quantité Facturée', readonly=True)
    quantity_free = fields.Float(string='Quantité Gratuite', readonly=True)

    # Coûts
    cost_total = fields.Float(string='Coût Total', readonly=True)
    cost_billed = fields.Float(string='Coût Facturé', readonly=True)
    cost_free = fields.Float(string='Coût Gratuit', readonly=True)

    # États
    consumed = fields.Boolean(string='Consommé', readonly=True)
    included_in_payment = fields.Boolean(string='Inclus dans le paiement', readonly=True)

    def _query(self):
        """Requête pour l'analyse des produits consommés"""
        return """
            SELECT 
                mc.id,
                DATE(ho.op_date) as date,
                mc.outpatient_id,
                mc.product_id,
                mc.consumed,
                mc.included_in_payment,

                -- Quantités
                mc.quantity as quantity_used,
                CASE 
                    WHEN mc.included_in_payment = true 
                    THEN mc.quantity 
                    ELSE 0 
                END as quantity_billed,
                CASE 
                    WHEN mc.included_in_payment = false 
                    THEN mc.quantity 
                    ELSE 0 
                END as quantity_free,

                -- Coûts
                mc.amount_total as cost_total,
                CASE 
                    WHEN mc.included_in_payment = true 
                    THEN mc.amount_total 
                    ELSE 0 
                END as cost_billed,
                CASE 
                    WHEN mc.included_in_payment = false 
                    THEN mc.amount_total 
                    ELSE 0 
                END as cost_free

            FROM medical_care mc
            JOIN hospital_outpatient ho ON mc.outpatient_id = ho.id
            WHERE mc.consumed = true
              AND ho.state != 'draft'
        """

    @property
    def _table_query(self):
        return self._query()

    def init(self):
        """Initialisation de la vue SQL"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW {self._table} as ({self._query()})""")