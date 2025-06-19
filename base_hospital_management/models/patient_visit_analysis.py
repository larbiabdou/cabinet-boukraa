# -*- coding: utf-8 -*-
################################################################################
#
#    Hospital Visit Analysis Report - Version Simple avec Filtrage Date
#
################################################################################
from odoo import api, fields, models, tools


class PatientVisitAnalysis(models.Model):
    """Analyse des visites patients avec filtrage par date"""
    _name = 'patient.visit.analysis'
    _description = 'Analyse des Visites Patients'
    _auto = False
    _rec_name = 'op_reference'
    _order = 'op_date desc'

    # Champs de base des visites pour filtrage
    op_reference = fields.Char(string='Référence OP', readonly=True)
    patient_id = fields.Many2one('res.partner', string='Patient', readonly=True)
    op_date = fields.Datetime(string='Date Visite', readonly=True)
    payment_state = fields.Selection([
        ('not_paid', 'Non payé'),
        ('in_payment', 'En paiement'),
        ('paid', 'Payé'),
    ], string='État Paiement', readonly=True)

    # Montants par visite
    amount = fields.Float(string='Montant Total', readonly=True)
    stock_expenses_visit = fields.Float(string='Dépenses Stock (visite)', readonly=True)
    stock_value_visit = fields.Float(string='Valeur Stock (visite)', readonly=True)
    gross_margin_visit = fields.Float(string='Marge Brute (visite)', readonly=True)
    visit_paid = fields.Integer(
        string='Visites payés',
        required=False)
    visit_unpaid = fields.Integer(
        string='Visites impayés',
        required=False)

    def _query(self):
        """Requête simple avec une ligne par visite"""
        return """
            SELECT 
                ho.id,
                ho.op_reference,
                ho.patient_id,
                ho.op_date,
                ho.payment_state,
                ho.amount,

                -- Dépenses stock (consommation non facturée) par visite
                COALESCE(SUM(CASE 
                    WHEN mc.consumed = true AND mc.included_in_payment = false 
                    THEN mc.amount_total 
                    ELSE 0 
                END), 0) as stock_expenses_visit,

                -- Valeur stock utilisé (tout: facturé et non facturé) par visite
                COALESCE(SUM(CASE 
                    WHEN mc.consumed = true 
                    THEN mc.amount_total 
                    ELSE 0 
                END), 0) as stock_value_visit,

                -- Marge Brute par visite = CA - Dépenses stock (non facturé)
                (ho.amount - COALESCE(SUM(CASE 
                    WHEN mc.consumed = true AND mc.included_in_payment = false 
                    THEN mc.amount_total 
                    ELSE 0 
                END), 0)) as gross_margin_visit,

                -- Mesures pour comptage des visites
                CASE WHEN ho.payment_state = 'paid' THEN 1 ELSE 0 END as visit_paid,
                CASE WHEN ho.payment_state = 'not_paid' THEN 1 ELSE 0 END as visit_unpaid

            FROM hospital_outpatient ho
            LEFT JOIN medical_care mc ON ho.id = mc.outpatient_id
            WHERE ho.state != 'draft'
            GROUP BY ho.id, ho.op_reference, ho.patient_id, ho.op_date, ho.payment_state, ho.amount
        """

    @property
    def _table_query(self):
        return self._query()

    def init(self):
        """Initialisation de la vue SQL"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW {self._table} as ({self._query()})""")