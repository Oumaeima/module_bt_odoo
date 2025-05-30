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
        group_expand='_read_group_stage_ids')
    technician_signature = fields.Binary(string="Signature Technicien")
    supervisor_signature = fields.Binary(string="Signature Superviseur")
    priority = fields.Selection(
        bt_stages.AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=bt_stages.AVAILABLE_PRIORITIES[0][0])
    schedule_date = fields.Date(string="Date Planifiée")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return stages.search([], order=order or 'sequence, id')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('gmao.bt') or 'New'

            if vals.get('technician_id') and not vals.get('stage_id'):
                assigned_stage = self.env['bt.stages'].search([('name', '=', 'Affecté')], limit=1)
                if assigned_stage:
                    vals['stage_id'] = assigned_stage.id

        return super().create(vals_list)

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


    @api.model
    def check_late_bt(self):
        today = fields.Date.context_today(self)

        # 1. BT en retard → notifier le technicien
        late_bts = self.search([
            ('stage_id.name', 'not in', ['Clôturé', 'Réalisé']),
            ('schedule_date', '!=', False),
            ('schedule_date', '<', today),
            ('technician_id', '!=', False)
        ])

        for bt in late_bts:
            technician = bt.technician_id
            msg = f"Le Bon de Travail « {bt.name} » est en retard (prévu le {bt.schedule_date})."

            # Notification interne
            bt.message_post(body=msg, subject="⚠️ BT en Retard", partner_ids=[technician.partner_id.id])

            # E-mail
            if technician.email:
                bt.message_post(
                    body=msg,
                    subject="Alerte : BT en Retard",
                    partner_ids=[technician.partner_id.id],
                    message_type='email'
                )