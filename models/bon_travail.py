from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bt_stages

class GmaoBonTravail(models.Model):
    _name = 'gmao.bt'
    _description = 'Bon de Travail'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Référence", required=True, default='New', copy=False)
    description = fields.Text(string="Description")
    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement concerné")
    intervention_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive'),
        ('inspection', 'Inspection'),
        ('other', 'Autre'),
    ], string="Type d'intervention")
    used_parts_ids = fields.Many2many('product.product', string="Pièces utilisées")
    technician_id = fields.Many2one('res.users', string="Technicien")
    supervisor_id = fields.Many2one('res.users', string="Superviseur")
    stage_id = fields.Many2one(
        'bt.stages',
        string='Étape',
        group_expand='_read_group_stage_ids',
        limit=1)
    technician_signature = fields.Binary(string="Signature Technicien")
    supervisor_signature = fields.Binary(string="Signature Superviseur")
    color = fields.Integer(string='Color Index')
    priority = fields.Selection(
        bt_stages.AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=bt_stages.AVAILABLE_PRIORITIES[0][0])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return stages.search([], order=order or 'sequence, id')


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('gmao.bt') or 'New'

        # Affecte automatiquement l'étape "Affecté" si un technicien est assigné
        if vals.get('technician_id') and not vals.get('stage_id'):
            assigned_stage = self.env['bt.stages'].search([('name', '=', 'Affecté')], limit=1)
            if assigned_stage:
                vals['stage_id'] = assigned_stage.id

        return super().create(vals)

    def write(self, vals):
        for rec in self:
            if 'technician_id' in vals and vals['technician_id'] and not vals.get('stage_id'):
                assigned_stage = self.env['bt.stages'].search([('name', '=', 'Affecté')], limit=1)
                if assigned_stage:
                    vals['stage_id'] = assigned_stage.id
        return super().write(vals)


    def action_print_bt(self):
        self.ensure_one()
        return self.env.ref('gmao.action_report_gmao_bt').report_action(self)

