from odoo import fields, models, api
from odoo.exceptions import ValidationError


class GenerateSerialWizard(models.TransientModel):
    _name = 'generate.serial.wizard'
    _description = 'Generate Serial Numbers'

    serial_count = fields.Integer(string="Serial Count")
    ticket_id = fields.Many2one('mrp.production', string='Ticket Id')
    product_id = fields.Many2one('product.product', string="Product Id")

    def generate_serial(self):
        self.ticket_id = self.env.context.get('active_id')
        seq_id = self.ticket_id.product_id.sequence_id

        if self.serial_count > self.ticket_id.product_qty:
            raise ValidationError("Cannot enter value greater than product quantity.")

        remaining = self.ticket_id.product_qty - len(self.ticket_id.serial_ids)
        if self.serial_count > remaining:
            raise ValidationError("Cannot generate more than remaining quantity.")

        for _ in range(self.serial_count):
            serial_no = seq_id.next_by_id()
            lot = self.env['stock.lot'].create({
                'name': serial_no,
                'product_id': self.ticket_id.product_id.id,
            })

            self.ticket_id.serial_ids = [(4, lot.id)]