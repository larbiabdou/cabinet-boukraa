# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date


class ResPartner(models.Model):
    """Inherited to add more fields and functions"""
    _inherit = 'res.partner'
    _description = 'Hospital Patients'
    _order = 'patient_seq asc'  # Tri alphabétique


    # Champs utilisés dans les vues
    is_patient = fields.Boolean(
        string='Is_patient',
        required=False)
    cin = fields.Char(
        string='CIN',
        required=False)

    date_of_birth = fields.Date(
        string='Date of Birth',
        help='Date of birth of the patient')

    blood_group = fields.Selection(
        string='Blood Group',
        help='Blood group of the patient',
        selection=[('a', 'A'), ('b', 'B'), ('o', 'O'), ('ab', 'AB')])

    rh_type = fields.Selection(
        selection=[('-', 'Négatif'), ('+', 'Positif')],
        string='RH Type',
        help='Rh type of the blood group')

    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female')],
        string='Gender',
        help='Gender of the patient')

    marital_status = fields.Selection(
        selection=[('enfant', 'Enfant'), ('married', 'Married'),
                   ('unmarried', 'Unmarried'), ('widow', 'Widow'),
                   ('widower', 'Widower'), ('divorcee', 'Divorcee')],
        string='Marital Status',
        help='Marital status of patient')

    patient_seq = fields.Char(
        string='Patient No.',
        help='Sequence number of the patient',
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: 'New')

    notes = fields.Html(
        string='Note',
        help='Notes regarding the notes',
        sanitize_style=True)

    profession = fields.Char(
        string='Profession',
        required=False)

    # Champs calculés et relations
    appointment_count = fields.Integer(
        string='Consultations',
        compute="compute_appointment_count",
        required=False)

    outpatient_ids = fields.One2many(
        comodel_name='hospital.outpatient',
        inverse_name='patient_id',
        string='Consultations',
        domain=[('state', '!=', 'draft')],
        required=False)

    outpatient_medecine_ids = fields.Many2many(
        comodel_name='hospital.outpatient',
        string='Ordonnance',
        compute="compute_outpatient_medecine_ids",
        required=False)

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True)

    age = fields.Integer(
        string='Age')

    age_str = fields.Char(
        string='Age',
        compute="compute_age")

    # Champs antécédents
    antecedents_chirurgicaux = fields.Text(
        string='Antécédents Chirurgicaux',
        help='Détails des antécédents chirurgicaux du patient')

    antecedents_medicaux = fields.Text(
        string='Antécédents Médicaux',
        help='Détails des antécédents médicaux du patient')

    antecedents_familiaux = fields.Text(
        string='Antécédents Familiaux',
        help='Détails des antécédents familiaux du patient')

    antecedents_allergiques = fields.Text(
        string='Antécédents Allergiques',
        help='Détails des antécédents allergiques du patient')

    firstname = fields.Char(
        string='Prénom',
        required=False)

    lastname = fields.Char(
        string='Nom',
        required=False)

    total_credit = fields.Float(
        string='Reste',
        compute="compute_total_credit",
        required=False)

    address = fields.Char(
        string='Adresse',
        required=False)

    # Contraintes SQL
    _sql_constraints = [
        ('unique_name_date_of_birth',
         'unique(name, date_of_birth)',
         'Un patient avec le même nom et la date de naissance existe déja'),
    ]

    # Méthodes compute
    def compute_outpatient_medecine_ids(self):
        """Calcule outpatient_medecine_ids à partir des outpatient_ids"""
        for record in self:
            outpatients_with_prescriptions = record.outpatient_ids.filtered(
                lambda op: op.prescription_ids
            )
            record.outpatient_medecine_ids = [(6, 0, outpatients_with_prescriptions.ids)]

    def compute_total_credit(self):
        for record in self:
            appointments = self.env['hospital.outpatient'].search([
                ('patient_id', '=', record.id),
                ('state', '!=', 'draft')
            ])
            record.total_credit = (
                                          sum(appointment.amount for appointment in appointments) -
                                          sum(appointment.amount_paid for appointment in appointments)
                                  ) or 0

    @api.onchange('firstname', 'lastname')
    def onchange_lastname_firstname(self):
        for record in self:
            record.name = ''
            if record.lastname:
                record.name = record.lastname
            if record.firstname:
                record.name += ' ' + record.firstname

    def compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                birth_date = fields.Date.from_string(record.date_of_birth)

                # Utilisation de relativedelta pour un calcul précis
                delta = relativedelta(today, birth_date)

                # Formatage selon l'âge
                if delta.years >= 1:
                    # Plus d'un an : afficher en années
                    record.age_str = f"{delta.years} an{'s' if delta.years > 1 else ''}"
                elif delta.months >= 1:
                    # Moins d'un an mais plus d'un mois : afficher en mois
                    record.age_str = f"{delta.months} mois"
                else:
                    # Moins d'un mois : afficher "1 mois"
                    record.age_str = "1 mois"
            else:
                record.age_str = "0"

    @api.depends('patient_seq', 'name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.patient_seq} / {record.name}"

    def compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['hospital.outpatient'].search_count([
                ('patient_id', '=', record.id),
                ('state', '!=', 'draft')
            ])

    # Méthodes CRUD et actions
    @api.model
    def create(self, vals):
        """Inherits create function for sequence generation"""
        if vals.get('patient_seq', 'New') == 'New':
            vals['patient_seq'] = self.env['ir.sequence'].next_by_code(
                'patient.sequence') or 'New'
        return super().create(vals)

    def action_view_appointmen(self):
        """Returns patient appointments"""
        self.ensure_one()
        return {
            'name': 'Consultations',
            'view_mode': 'tree,form',
            'res_model': 'hospital.outpatient',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id), ('state', '!=', 'draft')],
            'context': {'default_patient_id': self.id},
        }

    def name_get(self):
        """Returns the patient name"""
        result = []
        for rec in self:
            result.append((rec.id, f'{rec.patient_seq} - {rec.name}'))
        return result

    def action_schedule(self):
        """Returns form view of hospital appointment wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.outpatient',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'views': [[False, 'form']],
            'context': {
                'default_patient_id': self.id,
                'default_state': 'op'
            }
        }

    def action_appointment(self):
        """Returns form view of hospital appointment wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.outpatient',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [[False, 'form']],
            'context': {
                'default_patient_id': self.id,
                'default_state': 'op'
            }
        }


class MedicalAntecedent(models.Model):
    _name = 'medical.antecedent'
    _description = 'medical Antecedent'

    name = fields.Char()

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # Remplacer les contraintes existantes par des nouvelles (ou vides)
    _sql_constraints = [
        # Vous pouvez ajouter de nouvelles contraintes ici si besoin
        # ('new_constraint', 'CHECK(condition)', 'Message d\'erreur'),
    ]