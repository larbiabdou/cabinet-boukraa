from odoo import api, fields, models


class MedicalCare(models.Model):
    _name = 'medical.care'
    _description = 'Soins médicaux'

    outpatient_id = fields.Many2one(
        comodel_name='hospital.outpatient',
        string='outpatient_id',
        required=False)
    type_id = fields.Many2one(
        comodel_name='visit.type',
        string='Type_id',
        required=False)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Article',
        required=False)

    quantity = fields.Float(
        string='Quantité',
        required=False)

    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='UdM',
        domain="[('category_id', '=', product_uom_category_id)]",
        required=False)

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    
    consumed = fields.Boolean(
        string='Consommé',
        required=False)

    included_in_payment = fields.Boolean(
        string='Inclus dans le paiement',
        required=False)

    cost = fields.Float(
        string='Coût',
        required=False)

    amount_total = fields.Float(
        string='Amount total',
        compute="compute_total_amount",
        store=True,
        required=False)

    lot_id = fields.Many2one(
        comodel_name='stock.lot',
        string='Numéro de lot',
        domain="[('product_id', '=', product_id)]",
        required=False)

    tracking_required = fields.Selection(
        related='product_id.tracking',
        string='Suivi requis',
        readonly=True)

    @api.onchange('product_id')
    def _compute_uom_id(self):
        for record in self:
            record.uom_id = record.product_id.uom_id.id
            record.cost = record.product_id.standard_price
            record.lot_id = False

    @api.depends('cost', 'quantity')
    def compute_total_amount(self):
        for record in self:
            record.amount_total = record.cost * record.quantity



