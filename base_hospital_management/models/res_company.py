from odoo import api, fields, models


class ResCompany(models.Model):
    """Extension du modèle Company pour ajouter les informations du médecin"""
    _inherit = 'res.company'

    doctor_name = fields.Char(
        string='Nom du Médecin',
        help='Nom complet du médecin responsable')

    doctor_speciality = fields.Char(
        string='Spécialité',
        help='Spécialité médicale du médecin')

    doctor_order_number = fields.Char(
        string='N° d\'Ordre',
        help='Numéro d\'ordre du médecin au conseil de l\'ordre')

    facebook_page = fields.Char(
        string='Page Facebook',
        help='Nom de la page Facebook du cabinet')


class ResConfigSettings(models.TransientModel):
    """Extension des paramètres de configuration"""
    _inherit = 'res.config.settings'

    # Champs liés à la company
    doctor_name = fields.Char(
        string='Nom du Médecin',
        related='company_id.doctor_name',
        readonly=False,
        help='Nom complet du médecin responsable')

    doctor_speciality = fields.Char(
        string='Spécialité',
        related='company_id.doctor_speciality',
        readonly=False,
        help='Spécialité médicale du médecin')

    doctor_order_number = fields.Char(
        string='N° d\'Ordre',
        related='company_id.doctor_order_number',
        readonly=False,
        help='Numéro d\'ordre du médecin au conseil de l\'ordre')