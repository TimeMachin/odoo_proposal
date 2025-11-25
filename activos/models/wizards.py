from odoo import models, fields, api
from odoo.exceptions import UserError
import qrcode
import io
import base64
from datetime import datetime


class ActivosItemsWizardCrear(models.TransientModel):
    _name = 'activos.items.wizard.crear'
    _description = 'Wizard para crear múltiples items'

    nombre = fields.Char(
        string='Nombre del Item',
        required=True,
        help='Nombre que tendrán todos los items'
    )
    cantidad = fields.Integer(
        string='Cantidad de Items',
        required=True,
        default=1,
        help='Número de items a crear (1 a N)'
    )
    activo_fijo_padre_id = fields.Many2one(
        'activos.items',
        string='Activo Fijo Padre',
        help='El activo padre para estos items'
    )
    imprimir_etiquetas = fields.Boolean(
        string='Imprimir Etiquetas',
        default=False,
        help='Generar e imprimir automáticamente las etiquetas QR'
    )
    fecha_adquisicion = fields.Date(
        string='Fecha de Adquisición',
        help='Fecha de adquisición del activo fijo'
    )

    def _generar_codigo_qr(self, contenido):
        """Genera un código QR en base64 a partir del contenido"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(contenido)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

    def _generar_codigo_item_unico(self, padre_id, numero_secuencia):
        """Genera un código único basado en el padre y número de secuencia"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"ITEM-{padre_id}-{numero_secuencia}-{timestamp}"

    def action_crear_items(self):
        """Crea los items con los parámetros del wizard"""
        if self.cantidad < 1:
            raise UserError('La cantidad debe ser al menos 1')

        items_creados = []
        
        for i in range(1, self.cantidad + 1):
            # Asignar número de secuencia solo si hay más de 1 item
            numero_secuencia = i if self.cantidad > 1 else None
            
            # Generar código único
            codigo_item = self._generar_codigo_item_unico(
                self.activo_fijo_padre_id.id if self.activo_fijo_padre_id else 'NEW',
                numero_secuencia or 1
            )
            
            # Generar código QR
            codigo_qr = self._generar_codigo_qr(codigo_item)
            
            # Crear el item
            item = self.env['activos.items'].create({
                'activo_item_id': codigo_item,
                'nombre': f"{self.nombre}" + (f" ({i})" if self.cantidad > 1 else ""),
                'activo_fijo_padre_id': self.activo_fijo_padre_id.id if self.activo_fijo_padre_id else None,
                'numero_secuencia': numero_secuencia,
                'codigo_qr': codigo_qr,
            })
            items_creados.append(item)

        # Si se solicita imprimir etiquetas, generar reporte
        if self.imprimir_etiquetas and items_creados:
            return self._generar_reporte_etiquetas(items_creados)

        # Mostrar mensaje de confirmación
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': f'Se han creado {len(items_creados)} item(s) correctamente',
                'type': 'success',
            }
        }

    def _generar_reporte_etiquetas(self, items):
        """Genera un reporte con las etiquetas QR de los items"""
        # Por ahora retornamos una notificación
        # En producción, aquí iría la generación del reporte PDF
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Etiquetas Generadas',
                'message': f'Etiquetas QR generadas para {len(items)} item(s). Funcionalidad de impresión en desarrollo.',
                'type': 'info',
            }
        }


class ActivosItemsWizardInventario(models.TransientModel):
    _name = 'activos.items.wizard.inventario'
    _description = 'Wizard para inventario de items'

    codigo_qr_leido = fields.Char(
        string='Código QR',
        required=True,
        help='Escanea o ingresa el código QR del item'
    )
    notas = fields.Text(
        string='Notas',
        help='Notas adicionales del item'
    )
    crear_caso_mantenimiento = fields.Boolean(
        string='Crear Caso de Mantenimiento',
        default=False,
        help='Crear un caso de mantenimiento para este item'
    )
    descripcion_mantenimiento = fields.Text(
        string='Descripción de Mantenimiento',
        help='Descripción del caso de mantenimiento a crear'
    )

    def action_procesar_inventario(self):
        """Procesa el inventario del item escaneado"""
        # Buscar el item por código QR
        item = self.env['activos.items'].search([
            ('codigo_qr', '=', self.codigo_qr_leido)
        ], limit=1)

        if not item:
            raise UserError(f'No se encontró item con el código QR: {self.codigo_qr_leido}')

        # Actualizar fecha de último inventario
        item.write({
            'fecha_ultimo_inventario': fields.Date.today(),
            'notas': (item.notas or '') + f"\n[INVENTARIO {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.notas or ''}",
        })

        # Crear caso de mantenimiento si se solicita
        if self.crear_caso_mantenimiento and self.descripcion_mantenimiento:
            maintenance_model = self.env.get('maintenance.request')
            if maintenance_model:
                maintenance_model.create({
                    'name': f'Mantenimiento: {item.nombre}',
                    'description': self.descripcion_mantenimiento,
                    'equipment_id': item.id if hasattr(item, 'equipment_id') else None,
                })

        # Retornar la vista del item actualizado
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'activos.items',
            'res_id': item.id,
            'view_mode': 'form',
            'target': 'current',
        }


class ActivosItemsWizardBaja(models.TransientModel):
    _name = 'activos.items.wizard.baja'
    _description = 'Wizard para dar de baja items'

    codigo_qr_leido = fields.Char(
        string='Código QR',
        required=True,
        help='Escanea o ingresa el código QR del item'
    )
    motivo_baja = fields.Text(
        string='Motivo de la Baja',
        required=True,
        help='Razón por la cual se da de baja el item'
    )

    def action_procesar_baja(self):
        """Procesa la baja del item escaneado"""
        # Buscar el item por código QR
        item = self.env['activos.items'].search([
            ('codigo_qr', '=', self.codigo_qr_leido)
        ], limit=1)

        if not item:
            raise UserError(f'No se encontró item con el código QR: {self.codigo_qr_leido}')

        if item.fecha_baja:
            raise UserError(f'El item {item.nombre} ya ha sido dado de baja en {item.fecha_baja}')

        # Actualizar fecha de baja y agregar motivo a las notas
        notas_actualizadas = (item.notas or '') + f"\nMotivo baja: {self.motivo_baja}"
        
        item.write({
            'fecha_baja': fields.Date.today(),
            'notas': notas_actualizadas,
        })

        # Retornar la vista del item actualizado
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'activos.items',
            'res_id': item.id,
            'view_mode': 'form',
            'target': 'current',
        }
