from odoo import models, fields


class AbdominalUltrasoundReport(models.Model):
    _name = 'abdominal.ultrasound.report'
    _description = 'Compte Rendu d’Échographie Abdominale'
    _rec_name = 'patient_id'
    # Foie
    date = fields.Date(
        string='Date',
        default=fields.Date.today(),
        required=False)
    outpatient_id = fields.Many2one(
        comodel_name='hospital.outpatient',
        string='Visite',
        required=False)
    patient_id = fields.Many2one(
        comodel_name='res.partner',
        string='Patient',
        related='outpatient_id.patient_id',
        required=False)

    liver_texture = fields.Selection([
        ('homogeneous', 'Homogène'),
        ('heterogeneous', 'Hétérogène')
    ], string='Foie')

    liver_contours = fields.Selection([
        ('regular', 'Régulier'),
        ('irregular', 'Irrégulier')
    ], string='Contours')

    # Vésicule biliaire (VB)
    gallbladder_wall = fields.Selection([
        ('thin', 'Fine'),
        ('thick', 'Épaisse')
    ], string='Paroi')

    gallbladder_content = fields.Selection([
        ('alithiasic', 'Alithiasique'),
        ('lithiasic', 'Lithiasique')
    ], string='Contenu')

    # Voies biliaires intra-hépatiques (VBIH)
    vbih = fields.Selection([
        ('non_dilated', 'Non dilatées'),
        ('dilated', 'Dilatées')
    ], string='VBIH')

    # Rein droit
    right_kidney_position = fields.Selection([
        ('lumbar', 'Lombaire'),
        ('ectopic', 'Ectopique')
    ], string='Siège')

    right_kidney_texture = fields.Selection([
        ('homogeneous', 'Homogène'),
        ('heterogeneous', 'Hétérogène')
    ], string='Texture')

    right_kidney_size = fields.Selection([
        ('normal', 'Normale'),
        ('hypertrophy', 'Hypertrophie'),
        ('ectasia', 'Ectasie')
    ], string='Taille')

    right_kidney_cortico_sinus_differentiation = fields.Selection([
        ('yes', 'Oui'),
        ('no', 'Non')
    ], string='Bonne différenciation cortico-sinusale')

    right_kidney_hydronephrosis = fields.Selection([
        ('yes', 'Oui'),
        ('no', 'Non')
    ], string='Hydronéphrose')

    # Rein gauche
    left_kidney_position = fields.Selection([
        ('lumbar', 'Lombaire'),
        ('ectopic', 'Ectopique')
    ], string='Siège')

    left_kidney_texture = fields.Selection([
        ('homogeneous', 'Homogène'),
        ('heterogeneous', 'Hétérogène')
    ], string='Texture')

    left_kidney_size = fields.Selection([
        ('normal', 'Normale'),
        ('hypertrophy', 'Hypertrophie'),
        ('ectasia', 'Ectasie')
    ], string='Taille')

    left_kidney_cortico_sinus_differentiation = fields.Selection([
        ('yes', 'Oui'),
        ('no', 'Non')
    ], string='Bonne différenciation cortico-sinusale')

    left_kidney_hydronephrosis = fields.Selection([
        ('yes', 'Oui'),
        ('no', 'Non')
    ], string='Hydronéphrose')

    # Rate
    spleen_texture = fields.Selection([
        ('homogeneous', 'Homogène'),
        ('heterogeneous', 'Hétérogène')
    ], string='Rate')

    spleen_size = fields.Selection([
        ('normal', 'Normale'),
        ('splenomegaly', 'Splénomégalie')
    ], string='Taille')

    # Pancréas
    pancreas_texture = fields.Selection([
        ('homogeneous', 'Homogène'),
        ('heterogeneous', 'Hétérogène')
    ], string='Tête et Corps')

    wirsung_canal = fields.Selection([
        ('normal', 'Normale'),
        ('dilated', 'Dilaté')
    ], string='Canal de Wirsung')

    # Collection liquidienne intra-abdominale
    intra_abdominal_fluid_collection = fields.Selection([
        ('present', 'Présente'),
        ('absent', 'Absente')
    ], string='Collection Liquidienne Intra-Abdominale')

    # Conclusion
    conclusion = fields.Text(string='Conclusion')