# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HospitalPrescription(models.Model):
    """Modèle principal pour les ordonnances"""
    _name = 'hospital.prescription'
    _description = 'Ordonnance'
    _rec_name = 'name'
    _order = 'date desc'

    name = fields.Char(
        string='Référence',
        default='New',
        readonly=True,
        help='Référence de l\'ordonnance')

    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True,
        help='Date de création de l\'ordonnance')

    patient_id = fields.Many2one(
        'res.partner',
        related="outpatient_id.patient_id",
        help='Patient concerné par l\'ordonnance')

    outpatient_id = fields.Many2one(
        'hospital.outpatient',
        string='Consultation',
        help='Consultation liée à cette ordonnance')

    prescription_type = fields.Selection([
        ('normal', 'Ordonnance Normale'),
        ('souche', 'Ordonnance Souche')
    ], string='Type d\'ordonnance',
        default='normal',
        required=True,
        help='Type de l\'ordonnance')

    prescription_line_ids = fields.One2many(
        'prescription.line',
        'prescription_id',
        string='Lignes de prescription',
        help='Détails des médicaments prescrits')

    # state = fields.Selection([
    #     ('draft', 'Brouillon'),
    #     ('confirmed', 'Confirmée'),
    #     ('delivered', 'Délivrée')
    # ], string='État',
    #     default='draft',
    #     help='État de l\'ordonnance')

    notes = fields.Text(
        string='Notes',
        help='Notes additionnelles sur l\'ordonnance')

    @api.model_create_multi
    def create(self, vals_list):
        """Génération automatique de la référence selon le type"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                prescription_type = vals.get('prescription_type', 'normal')
                if prescription_type == 'souche':
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'hospital.prescription.souche')
                else:  # normal
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'hospital.prescription.normal')

        return super(HospitalPrescription, self).create(vals_list)

    # def action_confirm(self):
    #     """Confirmer l'ordonnance"""
    #     self.state = 'confirmed'
    #
    # def action_deliver(self):
    #     """Marquer comme délivrée"""
    #     self.state = 'delivered'
    #
    # def action_reset_to_draft(self):
    #     """Remettre en brouillon"""
    #     self.state = 'draft'

    def action_print(self):
        """Imprimer l'ordonnance"""
        return self.env.ref(
            'base_hospital_management.action_report_prescription'
        ).report_action(self)

    def get_prescription_data(self):
        """Préparer les données pour l'impression"""
        p_list = []
        for line in self.prescription_line_ids:
            p_list.append({
                'medicine': line.medicine_id.name or '',
                'forme': line.medicine_id.forme or '',
                'dosage': line.medicine_id.dosage or '',
                'posologie': line.posologie_id.name or '',
                'note': line.note_1 or '',
                'qsp': line.qsp_id.name or '',
                'qsp_note': line.qsp_note or '',
            })

        return {
            'datas': p_list,
            'date': self.date.strftime('%d/%m/%Y') if self.date else '',
            'patient_name': self.patient_id.name or '',
            'age': self.patient_id.age_str or '',
            'lastname': self.patient_id.lastname or '',
            'firstname': self.patient_id.firstname or '',
            'prescription_ref': self.name or '',
            'prescription_type': dict(self._fields['prescription_type'].selection).get(self.prescription_type, ''),
        }

class HospitalPosologie(models.Model):
    """Classe pour les posologies"""
    _name = 'hospital.posologie'
    _description = 'Posologie'
    _rec_name = 'name'

    name = fields.Char(
        string='Posologie',
        required=True,
        help='Description de la posologie')


class HospitalQsp(models.Model):
    """Classe pour les QSP (Quantité Suffisante Pour)"""
    _name = 'hospital.qsp'
    _description = 'QSP (Quantité Suffisante Pour)'
    _rec_name = 'name'

    name = fields.Char(
        string='QSP',
        required=True,
        help='Description du QSP')


class PrescriptionLine(models.Model):
    """Lignes de prescription"""
    _name = 'prescription.line'
    _description = 'Ligne de Prescription'

    prescription_id = fields.Many2one(
        'hospital.prescription',
        string='Ordonnance',
        required=True,
        ondelete='cascade',
        help='Ordonnance associée')

    medicine_id = fields.Many2one(
        'hospital.medecin',
        string='Médicament',
        required=True,
        help='Médicament ou vaccin prescrit')

    quantity = fields.Integer(
        string='Quantité',
        default=1,
        help="Nombre de médicaments pour la période")

    no_intakes = fields.Float(
        string='Prises',
        help="Quantité à prendre à chaque prise")

    posologie_id = fields.Many2one(
        'hospital.posologie',
        string='Posologie',
        required=False,
        help='Posologie du médicament')

    qsp_id = fields.Many2one(
        'hospital.qsp',
        string='QSP',
        required=False,
        help='Quantité Suffisante Pour')

    qsp_note = fields.Char(
        string='Note QSP',
        required=False,
        help='Note additionnelle pour le QSP')

    time = fields.Selection([
        ('once', 'Une fois par jour'),
        ('twice', 'Deux fois par jour'),
        ('thrice', 'Trois fois par jour'),
        ('morning', 'Le matin'),
        ('noon', 'À midi'),
        ('evening', 'Le soir')
    ], string='Fréquence',
        help='Intervalle de prise du médicament')

    note_1 = fields.Char(
        string='Note',
        required=False,
        help='Note sur la prescription')

    note = fields.Selection([
        ('before', 'Avant les repas'),
        ('after', 'Après les repas')
    ], string='Avant/Après repas',
        help='Prise avant ou après les repas')

    # Relations avec les autres modèles (maintenues pour compatibilité)
    date = fields.Datetime(
        string='Date',
        related='prescription_id.date',
        store=True,
        required=False)

    outpatient_id = fields.Many2one(
        'hospital.outpatient',
        string='Consultation',
        related='prescription_id.outpatient_id',
        store=True,
        help='Consultation liée')

    res_partner_id = fields.Many2one(
        'res.partner',
        string='Patient',
        related='prescription_id.patient_id',
        store=True,
        help='Patient concerné')