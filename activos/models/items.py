from odoo import models, fields


class ActivoItem(models.Model):
    _name = 'activos.items'
    _description = 'Activo Item'
    _rec_name = 'nombre'

    activo_item_id = fields.Char(
        string='ID Activo Item',
        required=True,
        unique=True,
        help='Identificador unico del activo'
    )
    activo_fijo_padre_id = fields.Many2one(
        'activos.items',
        string='Activo Fijo Padre',
        help='Referencia al activo fijo padre (para activos componentes)'
    )
    nombre = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre del activo'
    )
    numero_secuencia = fields.Integer(
        string='Numero de Secuencia',
        help='Numero de secuencia del activo'
    )
    codigo_qr = fields.Char(
        string='Cudigo QR',
        unique=True,
        help='Cudigo QR unico del activo'
    )
    fecha_ultimo_inventario = fields.Date(
        string='Fecha ultimo Inventario',
        help='Fecha del ultimo inventario realizado'
    )
    fecha_baja = fields.Date(
        string='Fecha de Baja',
        help='Fecha cuando el activo fue dado de baja'
    )
    notas = fields.Text(
        string='Notas',
        help='Notas adicionales del activo'
    )

    _sql_constraints = [
        ('activo_item_id_unique', 'unique(activo_item_id)', 'El ID del activo debe ser unico'),
        ('codigo_qr_unique', 'unique(codigo_qr)', 'El codigo QR debe ser unico'),
    ]

    def action_crear_items(self):
        """Abre el wizard para crear multiples items"""
        return {
            'name': 'Crear Items',
            'type': 'ir.actions.act_window',
            'res_model': 'activos.items.wizard.crear',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_activo_fijo_padre_id': self.id}
        }

    def action_inventario_items(self):
        """Abre el wizard para hacer inventario de items"""
        return {
            'name': 'Inventario de Items',
            'type': 'ir.actions.act_window',
            'res_model': 'activos.items.wizard.inventario',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_baja_item(self):
        """Abre el wizard para dar de baja un item"""
        return {
            'name': 'Baja de Item',
            'type': 'ir.actions.act_window',
            'res_model': 'activos.items.wizard.baja',
            'view_mode': 'form',
            'target': 'new',
        }
