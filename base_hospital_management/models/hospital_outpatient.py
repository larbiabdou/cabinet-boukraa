# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class HospitalOutpatient(models.Model):
    """Class holding Outpatient details"""
    _name = 'hospital.outpatient'
    _description = 'Hospital Outpatient'
    _rec_name = 'op_reference'
    _inherit = 'mail.thread'
    _order = 'op_date desc'

    # Champs de base utilisés dans les vues
    op_reference = fields.Char(
        string="OP Reference",
        readonly=True,
        default='New',
        help='Op reference number of the patient')

    patient_id = fields.Many2one(
        'res.partner',
        domain=[('patient_seq', 'not in', ['New', 'Employee', 'User'])],
        string='Patient ID',
        help='Id of the patient',
        required=True)

    doctor_id = fields.Many2one('doctor.allocation',
                                string='Doctor',
                                help='Select the doctor',
                                domain=[('slot_remaining', '>', 0),
                                        ('date', '=', fields.date.today()),
                                        ('state', '=', 'confirm')])
    op_date = fields.Datetime(default=lambda self: fields.Datetime.now(), string='Date',
                          help='Date of OP')

    state = fields.Selection(
        [('draft', 'Draft'), ('op', 'OP'), ('done', 'Terminé')],
        default='draft',
        string='State',
        help='State of the outpatient')

    # Champs liés au patient supprimés car les champs source n'existent plus dans res.partner

    # Champs médicaux
    reason = fields.Text(
        string='Reason',
        help='Reason for visiting hospital')

    consult_motif = fields.Text(
        string="Motif de consultation",
        required=False)

    clinic_exam = fields.Text(
        string="Examen clinique",
        required=False)

    note = fields.Html(
        string="Note",
        sanitize_style=True,
        required=False)

    note_2 = fields.Text(
        string='Note_2',
        required=False)

    # Champs biométriques
    taille2 = fields.Float(
        string='Taille',
        required=False)

    poids2 = fields.Float(
        string='Poids',
        required=False)

    bmi = fields.Char(
        string='BMI',
        compute="compute_bmi",
        digits=(16, 2),
        required=False)

    glycemie = fields.Char(
        string='Glycemie',
        required=False)

    # Champs financiers
    visit_amount = fields.Float(
        string='Montant de la visite',
        required=False)

    amount = fields.Float(
        string='Montant à payer',
        compute="compute_amount",
        store=True,
        required=False)

    amount_paid = fields.Float(
        string='Montant payé',
        tracking=True,
        required=False)

    care_amount = fields.Float(
        string='Montant de soins',
        compute="compute_care_amount",
        store=True,
        tracking=True,
        required=False)

    payment_state = fields.Selection(
        string='Etat de paiement',
        selection=[('not_paid', 'Non payé'),
                   ('in_payment', 'En paiement'),
                   ('paid', 'Payé')],
        default='not_paid',
        tracking=True,
        required=False)

    slot = fields.Float(string='Slot', help='Slot for the patient',
                        copy=False, readonly=True)

    # Relations avec les ordonnances
    prescription_normale_ids = fields.One2many(
        'hospital.prescription',
        'outpatient_id',
        string='Ordonnances Normales',
        domain=[('prescription_type', '=', 'normal')],
        help='Ordonnances normales de cette consultation')

    prescription_souche_ids = fields.One2many(
        'hospital.prescription',
        'outpatient_id',
        string='Ordonnances Souches',
        domain=[('prescription_type', '=', 'souche')],
        help='Ordonnances souches de cette consultation')

    # Champ calculé pour toutes les prescriptions (pour compatibilité)
    prescription_ids = fields.One2many(
        'hospital.prescription',
        'outpatient_id',
        string='Toutes les Ordonnances',
        help='Toutes les ordonnances de cette consultation')

    # Compteurs pour les boutons intelligents
    prescription_normale_count = fields.Integer(
        string='Nombre d\'ordonnances normales',
        compute='_compute_prescription_counts')

    prescription_souche_count = fields.Integer(
        string='Nombre d\'ordonnances souches',
        compute='_compute_prescription_counts')

    medical_care_ids = fields.One2many(
        comodel_name='medical.care',
        inverse_name='outpatient_id',
        string='Soins',
        required=False)

    visit_type_id = fields.Many2one(
        comodel_name='visit.type',
        string='Type de visite',
        required=False)

    test_lab_ids = fields.One2many(
        comodel_name='laboratory.test.line',
        inverse_name='outpatient_id',
        string='Test_lab_ids',
        required=False)

    test_ids = fields.Many2many(
        comodel_name='laboratory.test',
        string='Bilans')

    # Certificats médicaux
    leave_certificate_ids = fields.One2many(
        'medical.leave.certificate',
        'outpatient_id',
        string='Arrêts de travail')

    leave_extension_ids = fields.One2many(
        'medical.leave.extension',
        'outpatient_id',
        string='Prolongations')

    work_resumption_ids = fields.One2many(
        'medical.work.resumption',
        'outpatient_id',
        string='Reprises de travail')

    referral_letter_ids = fields.One2many(
        'medical.referral.letter',
        'outpatient_id',
        string='Lettres d\'orientation')

    medical_certificate_ids = fields.One2many(
        'medical.certificate',
        'outpatient_id',
        string='Certificats médicaux')

    # Compteurs pour boutons intelligents
    leave_certificate_count = fields.Integer(
        string='Nombre d\'arrêts',
        compute='_compute_certificate_counts',
        store=True)

    leave_extension_count = fields.Integer(
        string='Nombre de prolongations',
        compute='_compute_certificate_counts',
        store=True)

    work_resumption_count = fields.Integer(
        string='Nombre de reprises',
        compute='_compute_certificate_counts',
        store=True)

    referral_letter_count = fields.Integer(
        string='Nombre d\'orientations',
        compute='_compute_certificate_counts',
        store=True)

    medical_certificate_count = fields.Integer(
        string='Nombre de certificats',
        compute='_compute_certificate_counts',
        store=True)

    # Champs techniques
    button_consume_visible = fields.Boolean(
        string='button_consume_visible',
        compute="compute_button_consume_visible",
        required=False)

    visit_type = fields.Selection(
        string='Visit_type',
        selection=[('visit', 'Visit'),
                   ('hijama', 'hijama'),
                   ('acupuncture', 'acupuncture'),
                   ('soins', 'soins')],
        store=True,
        required=False)

    color = fields.Integer(
        'Color',
        compute='_compute_color')

    has_group_doctor = fields.Boolean(
        string='Has_group_doctor',
        compute="compute_has_group_doctor",
        default=lambda self: self._default_has_group_doctor(),
        required=False)

    # Champs conservés pour compatibilité/fonctionnalité
    active = fields.Boolean(
        string='Active',
        help='True for active patients',
        default=True)

    # Méthodes compute
    @api.depends('leave_certificate_ids', 'leave_extension_ids', 'work_resumption_ids',
                 'referral_letter_ids', 'medical_certificate_ids')
    def _compute_certificate_counts(self):
        for record in self:
            record.leave_certificate_count = len(record.leave_certificate_ids)
            record.leave_extension_count = len(record.leave_extension_ids)
            record.work_resumption_count = len(record.work_resumption_ids)
            record.referral_letter_count = len(record.referral_letter_ids)
            record.medical_certificate_count = len(record.medical_certificate_ids)

    @api.depends('visit_amount', 'care_amount')
    def compute_amount(self):
        for record in self:
            record.amount = record.visit_amount + record.care_amount

    @api.depends('medical_care_ids', 'medical_care_ids.consumed',
                 'medical_care_ids.included_in_payment', 'medical_care_ids.amount_total')
    def compute_care_amount(self):
        for record in self:
            record.care_amount = sum(
                line.amount_total for line in record.medical_care_ids.filtered(
                    lambda l: l.consumed and l.included_in_payment
                )
            )

    def compute_bmi(self):
        for record in self:
            if record.taille2 > 0:
                record.bmi = float_round(
                    record.poids2 / (record.taille2 / 100) ** 2, 2
                )
            else:
                record.bmi = 0

    def compute_has_group_doctor(self):
        for record in self:
            record.has_group_doctor = self.env.user.has_group(
                'base_hospital_management.base_hospital_management_group_doctor'
            )

    def _default_has_group_doctor(self):
        return self.env.user.has_group(
            'base_hospital_management.base_hospital_management_group_doctor'
        )

    def compute_button_consume_visible(self):
        for record in self:
            if not record.medical_care_ids or all(line.consumed for line in record.medical_care_ids):
                record.button_consume_visible = True
            else:
                record.button_consume_visible = False

    def _compute_color(self):
        for record in self:
            color_map = {
                'visit': 2,
                'hijama': 4,
                'acupuncture': 10,
                'soins': 6
            }
            record.color = color_map.get(record.visit_type, 0)

    # Méthodes onchange
    @api.onchange('amount_paid', 'amount')
    def _onchange_amount_paid(self):
        for record in self:
            if record.amount > 0:
                if record.amount_paid >= record.amount:
                    record.payment_state = 'paid'
                elif record.amount_paid > 0:
                    record.payment_state = 'in_payment'
                else:
                    record.payment_state = 'not_paid'

    @api.onchange('visit_type_id')
    def _onchange_visit_type_id(self):
        for record in self:
            for line in record.visit_type_id.medical_care_ids:
                record.medical_care_ids = [(0, 0, {
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'quantity': line.quantity,
                })]

    # Actions des boutons
    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_reset_to_op(self):
        for record in self:
            record.state = 'op'

    def action_confirm(self):
        """Button action for confirming an op"""
        self.state = 'op'

    # Actions pour créer les certificats
    def action_create_leave_certificate(self):
        return {
            'name': 'Certificat d\'arrêt de travail',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.leave.certificate',
            'view_mode': 'form',
            'view_id': self.env.ref('base_hospital_management.view_medical_leave_certificate_form').id,
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_outpatient_id': self.id,
                'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
            }
        }

    def action_create_leave_extension(self):
        return {
            'name': 'Prolongation d\'arrêt de travail',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.leave.extension',
            'view_mode': 'form',
            'view_id': self.env.ref('base_hospital_management.view_medical_leave_extension_form').id,
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_outpatient_id': self.id,
                'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
            }
        }

    def action_create_work_resumption(self):
        return {
            'name': 'Certificat de reprise de travail',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.work.resumption',
            'view_mode': 'form',
            'view_id': self.env.ref('base_hospital_management.view_medical_work_resumption_form').id,
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_outpatient_id': self.id,
                'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
            }
        }

    def action_create_referral_letter(self):
        return {
            'name': 'Lettre d\'orientation',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.referral.letter',
            'view_mode': 'form',
            'view_id': self.env.ref('base_hospital_management.view_medical_referral_letter_form').id,
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_outpatient_id': self.id,
                'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                'default_referral_reason': '',
            }
        }

    def action_create_medical_certificate(self):
        return {
            'name': 'Certificat médical',
            'type': 'ir.actions.act_window',
            'res_model': 'medical.certificate',
            'view_mode': 'form',
            'view_id': self.env.ref('base_hospital_management.view_medical_certificate_form').id,
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_outpatient_id': self.id,
                'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                'default_consultation_reason': '',
                'default_examination_result': '',
            }
        }

    # Actions pour boutons intelligents
    def action_view_leave_certificates(self):
        if self.leave_certificate_count == 1:
            certificate = self.leave_certificate_ids[0]
            return {
                'name': 'Certificat d\'arrêt de travail',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.leave.certificate',
                'res_id': certificate.id,
                'view_mode': 'form',
                'view_id': self.env.ref('base_hospital_management.view_medical_leave_certificate_form').id,
                'target': 'new',
            }
        else:
            return {
                'name': 'Arrêts de travail',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.leave.certificate',
                'view_mode': 'tree,form',
                'domain': [('outpatient_id', '=', self.id)],
                'context': {
                    'default_outpatient_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                }
            }

    def action_view_leave_extensions(self):
        if self.leave_extension_count == 1:
            extension = self.leave_extension_ids[0]
            return {
                'name': 'Prolongation d\'arrêt de travail',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.leave.extension',
                'res_id': extension.id,
                'view_mode': 'form',
                'view_id': self.env.ref('base_hospital_management.view_medical_leave_extension_form').id,
                'target': 'new',
            }
        else:
            return {
                'name': 'Prolongations d\'arrêt',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.leave.extension',
                'view_mode': 'tree,form',
                'domain': [('outpatient_id', '=', self.id)],
                'context': {
                    'default_outpatient_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                }
            }

    def action_view_work_resumptions(self):
        if self.work_resumption_count == 1:
            resumption = self.work_resumption_ids[0]
            return {
                'name': 'Certificat de reprise de travail',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.work.resumption',
                'res_id': resumption.id,
                'view_mode': 'form',
                'view_id': self.env.ref('base_hospital_management.view_medical_work_resumption_form').id,
                'target': 'new',
            }
        else:
            return {
                'name': 'Reprises de travail',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.work.resumption',
                'view_mode': 'tree,form',
                'domain': [('outpatient_id', '=', self.id)],
                'context': {
                    'default_outpatient_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                }
            }

    def action_view_referral_letters(self):
        if self.referral_letter_count == 1:
            letter = self.referral_letter_ids[0]
            return {
                'name': 'Lettre d\'orientation',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.referral.letter',
                'res_id': letter.id,
                'view_mode': 'form',
                'view_id': self.env.ref('base_hospital_management.view_medical_referral_letter_form').id,
                'target': 'new',
            }
        else:
            return {
                'name': 'Lettres d\'orientation',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.referral.letter',
                'view_mode': 'tree,form',
                'domain': [('outpatient_id', '=', self.id)],
                'context': {
                    'default_outpatient_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                }
            }

    def action_view_medical_certificates(self):
        if self.medical_certificate_count == 1:
            certificate = self.medical_certificate_ids[0]
            return {
                'name': 'Certificat médical',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.certificate',
                'res_id': certificate.id,
                'view_mode': 'form',
                'view_id': self.env.ref('base_hospital_management.view_medical_certificate_form').id,
                'target': 'new',
            }
        else:
            return {
                'name': 'Certificats médicaux',
                'type': 'ir.actions.act_window',
                'res_model': 'medical.certificate',
                'view_mode': 'tree,form',
                'domain': [('outpatient_id', '=', self.id)],
                'context': {
                    'default_outpatient_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_date': self.op_date.date() if self.op_date else fields.Date.today(),
                }
            }

    # Actions métier
    def consume_medical_care_ids(self):
        for record in self:
            location_production = self.env['stock.location'].search([('usage', '=', 'production')])
            data = []
            for line in record.medical_care_ids.filtered(lambda l: not l.consumed):
                data.append([0, 0, {
                    'name': 'Soins médicaux visite ' + record.op_reference,
                    'product_id': line.product_id.id,
                    'product_uom': line.uom_id.id,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': location_production.id,
                    'product_uom_qty': line.quantity,
                    'quantity': line.quantity,
                }])

            pick_output = self.env['stock.picking'].create({
                'picking_type_id': self.env.ref('stock.picking_type_out').id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': location_production.id,
                'origin': self.op_reference,
                'move_ids': data,
            })
            pick_output.button_validate()

            for line in record.medical_care_ids.filtered(lambda l: not l.consumed):
                line.consumed = True

    # Actions rapports
    def action_print_test_order(self):
        p_list = []
        for test in self.test_lab_ids:
            p_list.append({
                'name': test.test_id.name,
                'is_sub_test': test.is_sub_test,
            })

        data = {
            'datas': p_list,
            'date': self.op_date.strftime('%d/%m/%Y'),
            'patient_name': self.patient_id.name,
            'age': self.patient_id.age,
            'lastname': self.patient_id.lastname,
            'firstname': self.patient_id.firstname,
        }
        return self.env.ref(
            'base_hospital_management.action_report_test_order'
        ).report_action(self, data=data)

    # Modification de la méthode d'impression pour gérer les nouvelles ordonnances
    def action_print_prescription(self):
        """Imprimer toutes les ordonnances de la consultation"""
        all_prescriptions = self.prescription_ids
        if not all_prescriptions:
            return {'type': 'ir.actions.act_window_close'}

        # Si une seule ordonnance, l'imprimer directement
        if len(all_prescriptions) == 1:
            return all_prescriptions[0].action_print()

        # Sinon, ouvrir une fenêtre pour choisir
        return {
            'name': 'Choisir l\'ordonnance à imprimer',
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', all_prescriptions.ids)],
            'target': 'new',
        }

    # Actions schedule
    def action_schedule(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.outpatient',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [[False, 'form']],
            'context': {
                'default_patient_id': self.patient_id.id
            }
        }

    # Méthodes CRUD
    @api.model
    def create(self, vals):
        """Op number generator"""
        if vals.get('op_reference', 'New') == 'New':
            vals['op_reference'] = self.env['ir.sequence'].next_by_code(
                'hospital.outpatient') or 'New'
        return super().create(vals)

    def write(self, values):
        super().write(values)
        if 'test_ids' in values and values['test_ids']:
            for test in self.test_ids:
                if test.id not in self.test_lab_ids.mapped('test_id').ids:
                    lab_test = self.env['laboratory.test.line'].create({
                        'outpatient_id': self.id,
                        'test_id': test.id,
                        'name': test.name,
                        'is_sub_test': False,
                        'parent_test_id': False
                    })
                    for sub_test in test.sub_test_ids:
                        self.test_lab_ids = [(0, 0, {
                            'test_id': sub_test.id,
                            'name': ' ->   ' + sub_test.name,
                            'is_sub_test': True,
                            'parent_test_id': lab_test.id
                        })]

    # def unlink(self):
    #     for record in self:
    #         if record.state == 'done':
    #             raise ValidationError('Vous ne pouvez pas supprimer une consultation terminée')
    #     return super().unlink()


class VisiteType(models.Model):
    _name = 'visit.type'
    _description = 'Type de visite'

    name = fields.Char(string="Nom")
    medical_care_ids = fields.One2many(
        comodel_name='medical.care',
        inverse_name='type_id',
        string='Soins',
        required=False)


class LaboratoryTestLine(models.Model):
    _name = 'laboratory.test.line'
    _description = 'Laboratory Test Line'

    name = fields.Char(string='Name', required=False)
    outpatient_id = fields.Many2one(
        comodel_name='hospital.outpatient',
        string='Outpatient_id',
        required=False)
    test_id = fields.Many2one(
        comodel_name='laboratory.test',
        string='Test',
        required=False)
    result = fields.Char(string='Résultat', required=False)
    is_sub_test = fields.Boolean(string='Is Sub-Test', default=False)
    parent_test_id = fields.Many2one('laboratory.test.line', string="Parent Test")