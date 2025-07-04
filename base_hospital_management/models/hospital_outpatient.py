# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Subina P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import base64
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HospitalOutpatient(models.Model):
    """Class holding Outpatient details"""
    _name = 'hospital.outpatient'
    _description = 'Hospital Outpatient'
    _rec_name = 'op_reference'
    _inherit = 'mail.thread'
    _order = 'op_date desc'

    op_reference = fields.Char(string="OP Reference", readonly=True,
                               default='New',
                               help='Op reference number of the patient')
    patient_id = fields.Many2one('res.partner',
                                 domain=[('patient_seq', 'not in',
                                          ['New', 'Employee', 'User'])],
                                 string='Patient ID', help='Id of the patient',
                                 required=True)
    is_diabetic = fields.Boolean(
        string='Diabétique',
        related="patient_id.is_diabetic",
        store="True",
        required=False)
    is_hta = fields.Boolean(
        string='HTA',
        related="patient_id.is_hta",
        store="True",
        required=False)
    is_divers = fields.Boolean(
        string='Divers',
        related="patient_id.is_divers",
        store="True",
        required=False)
    doctor_id = fields.Many2one('doctor.allocation',
                                string='Doctor',
                                help='Select the doctor',
                                domain=[('slot_remaining', '>', 0),
                                        ('date', '=', fields.date.today()),
                                        ('state', '=', 'confirm')])
    op_date = fields.Datetime(default=lambda self: fields.Datetime.now(), string='Date',
                          help='Date of OP')

    reason = fields.Text(string='Reason', help='Reason for visiting hospital')
    # test_count = fields.Integer(string='Test Created',
    #                             help='Number of tests created for the patient',
    #                             compute='_compute_test_count')
    # test_ids = fields.One2many('lab.test.line', 'op_id',
    #                            string='Tests',
    #                            help='Tests for the patient')
    state = fields.Selection(
        [('draft', 'Draft'), ('op', 'OP'), ('done', 'Terminé')],
        default='draft', string='State', help='State of the outpatient')
    prescription_ids = fields.One2many('prescription.line',
                                       'outpatient_id',
                                       string='Prescription',
                                       help='Prescription for the patient')
    invoiced = fields.Boolean(default=False, string='Invoiced',
                              help='True for invoiced')
    invoice_id = fields.Many2one('account.move', copy=False,
                                 string='Invoice',
                                 help='Invoice of the patient')
    attachment_id = fields.Many2one('ir.attachment',
                                    string='Attachment',
                                    help='Attachments related to the'
                                         ' outpatient')
    active = fields.Boolean(string='Active', help='True for active patients',
                            default=True)
    slot = fields.Float(string='Slot', help='Slot for the patient',
                        copy=False, readonly=True)
    is_sale_created = fields.Boolean(string='Sale Created',
                                     help='True if sale order created')
    
    note = fields.Html(
        string="Note",
        sanitize_style=True,
        required=False)

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
                   ('paid', 'Payé'),],
        default='not_paid',
        tracking=True,
        required=False, )
    clinic_exam = fields.Text(
        string="Examen clinique",
        required=False)
    consult_motif = fields.Text(
        string="Motif de consultation",
        required=False)

    leave_certificate_ids = fields.One2many('medical.leave.certificate', 'outpatient_id',
                                            string='Arrêts de travail')
    leave_extension_ids = fields.One2many('medical.leave.extension', 'outpatient_id', string='Prolongations')
    work_resumption_ids = fields.One2many('medical.work.resumption', 'outpatient_id', string='Reprises de travail')
    referral_letter_ids = fields.One2many('medical.referral.letter', 'outpatient_id',
                                          string='Lettres d\'orientation')
    medical_certificate_ids = fields.One2many('medical.certificate', 'outpatient_id', string='Certificats médicaux')

    # Compteurs pour les boutons intelligents
    leave_certificate_count = fields.Integer(string='Nombre d\'arrêts', compute='_compute_certificate_counts',
                                             store=True)
    leave_extension_count = fields.Integer(string='Nombre de prolongations', compute='_compute_certificate_counts',
                                           store=True)
    work_resumption_count = fields.Integer(string='Nombre de reprises', compute='_compute_certificate_counts',
                                           store=True)
    referral_letter_count = fields.Integer(string='Nombre d\'orientations', compute='_compute_certificate_counts',
                                           store=True)
    medical_certificate_count = fields.Integer(string='Nombre de certificats',
                                               compute='_compute_certificate_counts', store=True)

    @api.depends('leave_certificate_ids', 'leave_extension_ids', 'work_resumption_ids', 'referral_letter_ids',
                 'medical_certificate_ids')
    def _compute_certificate_counts(self):
        for record in self:
            record.leave_certificate_count = len(record.leave_certificate_ids)
            record.leave_extension_count = len(record.leave_extension_ids)
            record.work_resumption_count = len(record.work_resumption_ids)
            record.referral_letter_count = len(record.referral_letter_ids)
            record.medical_certificate_count = len(record.medical_certificate_ids)

    # Actions pour créer les certificats (popup avec contexte)
    def action_create_leave_certificate(self):
        """Ouvre un popup pour créer un certificat d'arrêt de travail"""
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

    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_create_leave_extension(self):
        """Ouvre un popup pour créer une prolongation d'arrêt"""
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
        """Ouvre un popup pour créer un certificat de reprise"""
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
        """Ouvre un popup pour créer une lettre d'orientation"""
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
                'default_referral_reason': '',  # Champ obligatoire
            }
        }

    def action_create_medical_certificate(self):
        """Ouvre un popup pour créer un certificat médical"""
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
                'default_consultation_reason': '',  # Champ obligatoire
                'default_examination_result': '',  # Champ obligatoire
            }
        }

    # Actions pour les boutons intelligents (popup si count=1, liste sinon)
    def action_view_leave_certificates(self):
        """Ouvre popup si 1 certificat, liste sinon"""
        if self.leave_certificate_count == 1:
            # Un seul certificat : ouvrir en popup
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
            # Plusieurs certificats : ouvrir la liste
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
        """Ouvre popup si 1 prolongation, liste sinon"""
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
        """Ouvre popup si 1 reprise, liste sinon"""
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
        """Ouvre popup si 1 lettre, liste sinon"""
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
        """Ouvre popup si 1 certificat, liste sinon"""
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

    @api.depends('visit_amount', 'care_amount')
    def compute_amount(self):
        for record in self:
            record.amount = record.visit_amount + record.care_amount

    @api.depends('medical_care_ids', 'medical_care_ids.consumed', 'medical_care_ids.included_in_payment', 'medical_care_ids.amount_total')
    def compute_care_amount(self) :
        for record in self:
            record.care_amount = sum(line.amount_total for line in record.medical_care_ids.filtered(lambda l: l.consumed and l.included_in_payment))

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

    button_consume_visible = fields.Boolean(
        string='button_consume_visible',
        compue="compute_button_consume_visible",
        required=False)

    visit_type = fields.Selection(
        string='Visit_type',
        selection=[('visit', 'Visit'),
                   ('hijama', 'hijama'),('acupuncture', 'acupuncture'),('soins', 'soins'), ],
        #compute='compute_visit_type',
        store=True,
        required=False, )
    color = fields.Integer('Color', compute='_compute_color')

    count_abdominal_report = fields.Integer(
        string='Count_abdominal_report',
        compute='compute_count_abdominal_report',
        required=False)

    ta_sys = fields.Char(
        string='TA Systolique',
        required=False)
    ta_dia = fields.Char(
        string='TA Diastolique',
        required=False)
    poids = fields.Char(
        string='Poids',
        required=False)
    glycemie = fields.Char(
        string='Glycemie',
        required=False)

    taille = fields.Char(
        string='Taille',
        required=False)
    other = fields.Char(
        string='Autres',
        required=False)
    note_2 = fields.Text(
        string='Note_2',
        required=False)

    def compute_count_abdominal_report(self):
        for record in self:
            record.count_abdominal_report = self.env['abdominal.ultrasound.report'].search_count([('outpatient_id', '=', record.id)])

    def action_view_abdominal_report(self):
        self.ensure_one()
        reports = self.env['abdominal.ultrasound.report'].search([('outpatient_id', '=', self.id)])

        action = {
            'res_model': 'abdominal.ultrasound.report',
            'type': 'ir.actions.act_window',
            'context': {'default_outpatient_id': self.id, 'default_patient_id': self.patient_id.id}
        }
        if len(reports) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': reports[0].id,
            })
        else:
            action.update({
                'name': "Compte rendu d’échographie abdominal",
                'domain': [('id', 'in', reports.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def _default_has_group_doctor(self):
        if self.env.user.has_group('base_hospital_management.base_hospital_management_group_doctor'):
            return True
        else:
            return False

    has_group_doctor = fields.Boolean(
        string='Has_group_doctor',
        compute="compute_has_group_doctor",
        default=_default_has_group_doctor,
        required=False)

    def compute_has_group_doctor(self):
        for record in self:
            if self.env.user.has_group('base_hospital_management.base_hospital_management_group_doctor'):
                record.has_group_doctor = True
            else:
                record.has_group_doctor = False

    def _compute_color(self):
        for record in self:
            if record.visit_type == 'visit':
                record.color = 2  # Vert
            elif record.visit_type == 'hijama':
                record.color = 4  # Bleu
            elif record.visit_type == 'acupuncture':
                record.color = 10
            elif record.visit_type == 'soins':
                record.color = 6

    def action_schedule(self):
        """Returns form view of hospital appointment wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.outpatient',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'views': [[False, 'form']],
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_state': 'op'
            }
        }

    def compute_button_consume_visible(self):
        for record in self:
            # Si pas de soins ou tous les soins sont consommés, cacher le bouton
            if not record.medical_care_ids or all(line.consumed for line in record.medical_care_ids):
                record.button_consume_visible = True
            else:
                # Si il y a des soins non consommés, afficher le bouton
                record.button_consume_visible = False

    # @api.depends('test_ids')
    # def onchange_test_lab_group(self):
    #     for record in self:
    #         for test in record.test_ids:
    #             test_id = test.id or test._origin.id
    #             # if test_id not in record.test_lab_ids.mapped('test_id').ids:
    #             record.test_lab_ids = [(0, 0, {
    #                 'test_id': test_id,
    #                 'name': test.name,
    #                 'is_sub_test': False,  # Indique qu'il s'agit d'un test principal
    #                 'parent_test_id': False
    #             })]
    #             for sub_test in test._origin.sub_test_ids:
    #                 record.test_lab_ids = [(0, 0, {
    #                     'test_id': sub_test._origin.id,
    #                     'name': ' ->   ' + sub_test.name,
    #                     'is_sub_test': True,  # Indique qu'il s'agit d'un test principal
    #                     'parent_test_id': test_id
    #
    #                 })]
    def write(self, values):
        # Add code here
        super(HospitalOutpatient, self).write(values)
        if 'test_ids' in values and values['test_ids']:
            for test in self.test_ids:
                if test.id not in self.test_lab_ids.mapped('test_id').ids:
                    lab_test = self.env['laboratory.test.line'].create({
                        'outpatient_id': self.id,
                        'test_id': test.id,
                        'name': test.name,
                        'is_sub_test': False,  # Indique qu'il s'agit d'un test principal
                        'parent_test_id': False
                    })
                    for sub_test in test.sub_test_ids:
                        self.test_lab_ids = [(0, 0, {
                            'test_id': sub_test.id,
                            'name': ' ->   ' + sub_test.name,
                            'is_sub_test': True,  # Indique qu'il s'agit d'un test principal
                            'parent_test_id': lab_test.id
                        })]

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
                #'name': 'Soins',
                'picking_type_id': self.env.ref('stock.picking_type_out').id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': location_production.id,
                'origin': self.op_reference,
                'move_ids': data,
            })
            pick_output.button_validate()
            for line in record.medical_care_ids.filtered(lambda l: not l.consumed):
                line.consumed = True

    

    @api.onchange('visit_type_id')
    def _onchange_visit_type_id(self):
        for record in self:
            for line in record.visit_type_id.medical_care_ids:
                record.medical_care_ids = [(0, 0, {
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'quantity': line.quantity,
                })]

    @api.model
    def create(self, vals):
        """Op number generator"""
        if vals.get('op_reference', 'New') == 'New':
            last_op = self.search([
                ('doctor_id', '=', vals.get('doctor_id')),
                ('op_reference', '!=', 'New'),
            ], order='create_date desc', limit=1)
            if last_op:
                last_number = int(last_op.op_reference[2:])
                new_number = last_number + 1
                vals['op_reference'] = f'OP{str(new_number).zfill(3)}'
            else:
                vals['op_reference'] = 'OP001'
        # if self.search([
        #     ('patient_id', '=', vals['patient_id']),
        # ]):
        #     raise ValidationError(
        #         'An OP already exists for this patient under the specified '
        #         'allocation')
        return super().create(vals)

    # @api.depends('test_ids')
    # def _compute_test_count(self):
    #     """Computes the value of test count"""
    #     self.test_count = len(self.test_ids.ids)
    #
    # @api.onchange('op_date')
    # def _onchange_op_date(self):
    #     """Method for updating the doamil of doctor_id"""
    #     self.doctor_id = False
    #     return {'domain': {'doctor_id': [('slot_remaining', '>', 0),
    #                                      ('date', '=', self.op_date),
    #                                      ('state', '=', 'confirm'), (
    #                                          'patient_type', 'in',
    #                                          [False, 'outpatient'])]}}

    @api.model
    def action_row_click_data(self, op_reference):
        """Returns data to be displayed on clicking op row"""
        op_record = self.env['hospital.outpatient'].sudo().search(
            [('op_reference', '=', op_reference),
             ('active', 'in', [True, False])])
        op_data = [op_reference, op_record.patient_id.patient_seq,
                   op_record.patient_id.name, str(op_record.op_date),
                   op_record.slot, op_record.reason,
                   op_record.doctor_id.doctor_id.name,
                   op_record.is_sale_created]
        medicines = []
        for rec in op_record.prescription_ids:
            medicines.append(
                [rec.medicine_id.name, rec.no_intakes, rec.time, rec.note,
                 rec.quantity, rec.medicine_id.id])
        return {
            'op_data': op_data,
            'medicines': medicines
        }

    # @api.model
    # def create_medicine_sale_order(self, order_id):
    #     """Method for creating sale order for medicines"""
    #     order = self.sudo().search([('op_reference', 'ilike', order_id)])
    #     sale_order = self.env['sale.order'].sudo().create({
    #         'partner_id': order.patient_id.id,
    #     })
    #     for i in order.prescription_ids:
    #         self.env['sale.order.line'].sudo().create({
    #             'product_id': i.medicine_id.id,
    #             'product_uom_qty': i.quantity,
    #             'order': sale_order.id,
    #         })
    #         self.create_invoice()

    @api.model
    def create_file(self, rec_id):
        """Method for creating prescription"""
        record = self.env['hospital.outpatient'].sudo().browse(rec_id)
        p_list = []
        data = False
        for rec in record.prescription_ids:
            p_list.append({
                'medicine': rec.medicine_id.name,
                'intake': rec.no_intakes,
                'time': rec.time.capitalize(),
                'quantity': rec.quantity,
                'note': rec.note.capitalize() if rec.note else '',
            })
            data = {
                'datas': p_list,
                'date': record.op_date,
                'patient_name': record.patient_id.name,
                'doctor_name': record.doctor_id.doctor_id.name,
            }
        pdf = self.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'base_hospital_management.action_report_patient_prescription',
            rec_id, data=data)
        record.attachment_id = self.env['ir.attachment'].sudo().create({
            'datas': base64.b64encode(pdf[0]),
            'name': "Prescription",
            'type': 'binary',
            'res_model': 'hospital.outpatient',
            'res_id': rec_id,
        })
        return {
            'url': f'/web/content'
                   f'/{record.attachment_id.id}?download=true&amp'
                   f';access_token=',
        }

    @api.model
    def create_new_out_patient(self, kw):
        """Create out patient from receptionist dashboard"""
        if kw['id']:
            partner = self.env['res.partner'].sudo().search(
                [
                    #'|', ('barcode', '=', kw['id']),
                 ('phone', '=', kw['op_phone'])])
            self.sudo().create({
                'patient_id': partner.id,
                'op_date': kw['date'],
                'reason': kw['reason'],
                'slot': kw['slot'],
                'doctor_id': kw['doctor'],
            })

    def action_create_lab_test(self):
        """Button action for creating a lab test"""
        return {
            'name': 'Create Lab Test',
            'res_model': 'lab.test.line',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'default_patient_type': 'outpatient',
                'default_op_id': self.id
            }
        }

    def action_view_test(self):
        """Method for viewing all lab tests"""
        return {
            'name': 'Created Tests',
            'res_model': 'lab.test.line',
            'view_mode': 'tree,form',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [
                ('patient_type', '=', 'outpatient'),
                ('op_id', '=', self.id)
            ]
        }

    # def action_convert_to_inpatient(self):
    #     """Converts an outpatient to inpatient"""
    #     self.state = 'inpatient'
    #     return {
    #         'name': 'Convert to Inpatient',
    #         'res_model': 'hospital.inpatient',
    #         'view_mode': 'form',
    #         'target': 'current',
    #         'type': 'ir.actions.act_window',
    #         'context': {
    #             'default_patient_id': self.patient_id.id,
    #             'default_attending_doctor_id': self.doctor_id.doctor_id.id,
    #         }
    #     }
    #
    # def action_op_cancel(self):
    #     """Button action for cancelling an op"""
    #     self.state = 'cancel'

    def action_confirm(self):
        """Button action for confirming an op"""
        if self.doctor_id.latest_slot == 0:
            self.slot = self.doctor_id.work_from
        else:
            self.slot = self.doctor_id.latest_slot + self.doctor_id.time_avg
        self.doctor_id.latest_slot = self.slot
        self.state = 'op'
    #
    # def create_invoice(self):
    #     """Method for creating invoice"""
    #     self.state = 'invoice'
    #     self.invoice_id = self.env['account.move'].sudo().create({
    #         'move_type': 'out_invoice',
    #         'date': fields.Date.today(),
    #         'invoice_date': fields.Date.today(),
    #         'partner_id': self.patient_id.id,
    #         'invoice_line_ids': [(
    #             0, 0, {
    #                 'name': 'Consultation fee',
    #                 'quantity': 1,
    #                 'price_unit': self.doctor_id.doctor_id.consultancy_charge,
    #             }
    #         )]
    #     })
    #     self.invoiced = True

    # def action_view_invoice(self):
    #     """Method for viewing invoice"""
    #     return {
    #         'name': 'Invoice',
    #         'domain': [('id', '=', self.invoice_id.id)],
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'tree,form',
    #         'context': {'create': False},
    #     }

    def action_print_test_order(self):
        """Method for printing prescription"""
        data = False
        p_list = []
        for test in self.test_lab_ids:
            if not test.is_sub_test:
                datas = {
                    'name': test.test_id.name,
                    'is_sub_test': False,
                }
                p_list.append(datas)
            else:
                datas = {
                    'name': test.test_id.name,
                    'is_sub_test': True,
                }
                p_list.append(datas)

        data = {
            'datas': p_list,
            'date': self.op_date.strftime('%d/%m/%Y'),
            'patient_name': self.patient_id.name,
            'age': self.patient_id.age,
            'lastname': self.patient_id.lastname,
            'firstname': self.patient_id.firstname,
            # 'doctor_name': self.doctor_id.doctor_id.name,
        }
        return self.env.ref(
            'base_hospital_management.action_report_test_order'). \
            report_action(self, data=data)

    def action_print_prescription(self):
        """Method for printing prescription"""
        data = False
        p_list = []
        for rec in self.prescription_ids:
            datas = {
                'medicine': rec.medicine_id.name,
                'forme': rec.medicine_id.forme,
                'dosage': rec.medicine_id.dosage,
                #'intake': rec.no_intakes,
                #'time': time.capitalize(),
                #'quantity': rec.quantity,
                'posologie': rec.posologie_id.name,
                'note': rec.note_1,
                'qsp': rec.qsp_id.name,
            }
            p_list.append(datas)
        data = {
            'datas': p_list,
            'date': self.op_date.strftime('%d/%m/%Y'),
            'patient_name': self.patient_id.name,
            'age': self.patient_id.age,
            'lastname': self.patient_id.lastname,
            'firstname': self.patient_id.firstname,
            #'doctor_name': self.doctor_id.doctor_id.name,
        }
        return self.env.ref(
            'base_hospital_management.action_report_patient_prescription'). \
            report_action(self, data=data)
    

class VisiteType(models.Model):
    _name = 'visit.type'
    _description = 'Type de visite'

    name = fields.Char(string="Nom")

    medical_care_ids = fields.One2many(
        comodel_name='medical.care',
        inverse_name='type_id',
        string='Soins',
        required=False)


class laboratoryTestLine(models.Model):
    _name = 'laboratory.test.line'
    _description = 'laboratory Test Line'

    name = fields.Char(
        string='Name',
        required=False)

    outpatient_id = fields.Many2one(
        comodel_name='hospital.outpatient',
        string='Outpatient_id',
        required=False)

    test_id = fields.Many2one(
        comodel_name='laboratory.test',
        string='Test',
        required=False)

    result = fields.Char(
        string='Résultat',
        required=False)
    is_sub_test = fields.Boolean(string='Is Sub-Test', default=False)
    parent_test_id = fields.Many2one('laboratory.test.line', string="Parent Test")  # Test parent, pour les sous-tests



    

