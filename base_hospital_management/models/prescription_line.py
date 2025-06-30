# -*- coding: utf-8 -*-
from odoo import fields, models


class HospitalPosologie(models.Model):
    """Classe pour les posologies"""
    _name = 'hospital.posologie'
    _description = 'Posologie'
    _rec_name = 'name'

    name = fields.Char(string='Posologie', required=True, help='Description de la posologie')


class HospitalQsp(models.Model):
    """Classe pour les QSP (Quantité Suffisante Pour)"""
    _name = 'hospital.qsp'
    _description = 'QSP (Quantité Suffisante Pour)'
    _rec_name = 'name'

    name = fields.Char(string='QSP', required=True, help='Description du QSP')


class PrescriptionLine(models.Model):
    """Class holding prescription line details"""
    _name = 'prescription.line'
    _description = 'Prescription Lines'

    medicine_id = fields.Many2one('hospital.medecin',
                                  string='Medicine', required=True,
                                  help='Medicines or vaccines')
    quantity = fields.Integer(string='Quantity',
                              help="The number of medicines for the time "
                                   "period")
    no_intakes = fields.Float(string='Intakes',
                              help="How much medicine want to take")
    qsp_id = fields.Many2one('hospital.qsp', string='QSP', required=False,
                             help='Quantité Suffisante Pour')
    posologie_id = fields.Many2one('hospital.posologie', string='Posologie', required=False,
                                   help='Posologie du médicament')
    date = fields.Datetime(
        string='Date',
        related='outpatient_id.op_date',
        required=False)
    time = fields.Selection(
        [('once', 'Une fois par jour'), ('twice', 'Deux fois par jour'),
         ('thrice', 'Trois fois par jour'), ('morning', 'Le matin'),
         ('noon', 'À midi'), ('evening', 'Le soir')], string='Time',
        help='The interval for medicine intake')
    note_1 = fields.Char(
        string='Note',
        required=False)
    note = fields.Selection(
        [('before', 'Avant les repas'), ('after', 'Après les repas')],
        string='Before/ After Food',
        help='Whether the medicine to be taken before or after food')
    inpatient_id = fields.Many2one('hospital.inpatient',
                                   string='Inpatient',
                                   help='The inpatient corresponds to the '
                                        'prescription line')
    outpatient_id = fields.Many2one('hospital.outpatient',
                                    string='Outpatient',
                                    help='The outpatient corresponds to the '
                                         'prescription line')
    res_partner_id = fields.Many2one('res.partner',
                                     string='Patient',
                                     help='The outpatient corresponds to the '
                                          'prescription line',
                                     related='outpatient_id.patient_id')