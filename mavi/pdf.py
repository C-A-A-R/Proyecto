from import_export.formats.base_formats import Format
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from io import BytesIO

class PDFDataUser(Format):
    def get_title(self):
        return "pdf"

    def get_extension(self):
        return "pdf"

    def get_content_type(self):
        return "application/pdf"

    def export_data(self, dataset, **kwargs):
        buffer = BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=landscape(A3))
        width, height = landscape(A3)

        # Márgenes simétricos izquierdo y derecho
        margin_x = 30  
        x = margin_x  # Usamos el margen izquierdo como base
        y = height - 50  # Margen superior estándar

        # Título del documento
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(x, y, "Exportación de Datos de Usuario")
        y -= 40

        # Ancho de las columnas considerando los márgenes izquierdo y derecho
        column_widths = self.calculate_column_widths(dataset, width - 2 * margin_x)  # Restar márgenes
        row_height = 20  # Altura de cada fila
        padding_x = 5  # Espacio de margen entre el texto y los bordes de las celdas en el eje X

        # Escribir los nombres de las columnas y dibujar las celdas
        pdf_canvas.setFont("Helvetica-Bold", 11)
        for i, col in enumerate(dataset.headers):
            pdf_canvas.drawString(x + sum(column_widths[:i]) + padding_x, y + 5, col)  # Subimos el texto un poco en Y (+5)

        # Dibujar la fila de los headers
        self.draw_row_borders(pdf_canvas, x, y, column_widths, row_height)
        y -= row_height

        # Escribir los datos y dibujar las celdas
        pdf_canvas.setFont("Helvetica", 11)
        for row in dataset.dict:
            if y < 50:  # Saltar a una nueva página si la posición es muy baja
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica-Bold", 11)
                y = height - 50  # Reiniciar Y para la nueva página
                
                # Dibujar los encabezados en la nueva página
                for i, col in enumerate(dataset.headers):
                    pdf_canvas.drawString(x + sum(column_widths[:i]) + padding_x, y + 5, col)  # Subimos el texto un poco en Y
                self.draw_row_borders(pdf_canvas, x, y, column_widths, row_height)
                y -= row_height
                pdf_canvas.setFont("Helvetica", 11)

            # Imprimir los valores de cada columna y dibujar las celdas
            for i, col in enumerate(dataset.headers):
                pdf_canvas.drawString(x + sum(column_widths[:i]) + padding_x, y + 5, str(row[col]))  # Subimos el texto un poco en Y

            # Dibujar la fila de datos
            self.draw_row_borders(pdf_canvas, x, y, column_widths, row_height)
            y -= row_height

        # Terminar el PDF
        pdf_canvas.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def calculate_column_widths(self, dataset, total_width):
        """
        Calcular los anchos de las columnas dinámicamente basado en el contenido.
        Asignamos menos espacio a columnas como "Nombre" y "Apellido" y más a columnas como "Correo".
        """
        column_names = dataset.headers
        num_columns = len(column_names)

        # Distribuir espacio basado en el contenido esperado
        column_width_ratios = {
            'Nombre de Usuario': 1.5,
            'Nombre': 1.3,
            'Apellido': 1.3,
            'Ultimo Inicio de Sesión': 2.1,
            'Correo': 2.7,
            'Fecha de Registro': 2.1,
            'Numero de Telefono': 2.1,
            'Sector de vivienda': 1.5,
            'Estado de Usuario': 1.0
        }

        # Total de los ratios definidos
        total_ratio = sum(column_width_ratios.get(col, 1.0) for col in column_names)

        # Calcular el ancho de cada columna basado en el total disponible
        column_widths = [
            (column_width_ratios.get(col, 1.0) / total_ratio) * total_width  # Total width ya incluye el espacio sin márgenes
            for col in column_names
        ]

        return column_widths

    def draw_row_borders(self, pdf_canvas, x, y, column_widths, row_height):
        """
        Dibujar las líneas horizontales y verticales para crear celdas en cada fila.
        """
        # Dibujar la línea inferior de la fila actual
        pdf_canvas.line(x, y, x + sum(column_widths), y)

        # Dibujar las líneas verticales para cada celda
        for i in range(len(column_widths) + 1):
            pdf_canvas.line(x + sum(column_widths[:i]), y, x + sum(column_widths[:i]), y + row_height)

        # Dibujar la línea superior (solo es necesario si es la fila de encabezado)
        pdf_canvas.line(x, y + row_height, x + sum(column_widths), y + row_height)

    def is_binary(self):
        return True
    
    
class PDFPayment(Format):
    def get_title(self):
        return "pdf"

    def get_extension(self):
        return "pdf"

    def get_content_type(self):
        return "application/pdf"

    def export_data(self, dataset, **kwargs):
        buffer = BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=landscape(A3))
        width, height = landscape(A3)

        # Márgenes simétricos izquierdo y derecho
        margin_x = 30  
        x = margin_x  # Usamos el margen izquierdo como base
        y = height - 50  # Margen superior estándar

        # Título del documento
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(x, y, "Exportación de Datos de Pagos")
        y -= 40

        # Ancho de las columnas considerando los márgenes izquierdo y derecho
        column_widths = self.calculate_column_widths(dataset, width - 2 * margin_x)  # Restar márgenes
        row_height = 20  # Altura de cada fila
        padding_x = 5  # Espacio de margen entre el texto y los bordes de las celdas en el eje X

        # Escribir los nombres de las columnas y dibujar las celdas
        pdf_canvas.setFont("Helvetica-Bold", 11)
        # Cambiar 'Días de Transmisión' a 'Días Trans.' en el dataset.headers
        dataset.headers = ['ID de Usuario', 'Nombre', 'Apellido', 'Nombre de Publicidad', 'Días Trans.', 'Fecha de Pago', 'Referencia de Pago', 'Estado de Pago']
        for i, col in enumerate(dataset.headers):
            pdf_canvas.drawString(x + sum(column_widths[:i]) + padding_x, y + 5, col)  # Subimos el texto un poco en Y (+5)

        # Dibujar la fila de los headers
        self.draw_row_borders(pdf_canvas, x, y, column_widths, row_height)
        y -= row_height

        # Escribir los datos y dibujar las celdas
        pdf_canvas.setFont("Helvetica", 11)
        for row in dataset.dict:
            if y < 50:  # Saltar a una nueva página si la posición es muy baja
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica-Bold", 11)
                y = height - 50  # Reiniciar Y para la nueva página
                
                # Dibujar los encabezados en la nueva página
                for i, col in enumerate(dataset.headers):
                    pdf_canvas.drawString(x + sum(column_widths[:i]) + padding_x, y + 5, col)  # Subimos el texto un poco en Y
                self.draw_row_borders(pdf_canvas, x, y, column_widths, row_height)
                y -= row_height
                pdf_canvas.setFont("Helvetica", 11)

            # Imprimir los valores de cada columna y dibujar las celdas
            for i, col in enumerate(dataset.headers):
                pdf_canvas.drawString(x + sum(column_widths[:i]) + padding_x, y + 5, str(row[col]))  # Subimos el texto un poco en Y

            # Dibujar la fila de datos
            self.draw_row_borders(pdf_canvas, x, y, column_widths, row_height)
            y -= row_height

        # Terminar el PDF
        pdf_canvas.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def calculate_column_widths(self, dataset, total_width):
        """
        Calcular los anchos de las columnas dinámicamente basado en el contenido.
        Asignamos menos espacio a columnas como "Nombre" y "Apellido" y más a columnas como "Fecha de Pago" o "Referencia de Pago".
        """
        column_names = dataset.headers

        # Definir nuevos ratios basados en la longitud de los datos
        column_width_ratios = {
            'ID de Usuario': 1.0,            # Dato pequeño
            'Nombre': 1.5,                   # Dato moderado
            'Apellido': 1.5,                 # Dato moderado
            'Nombre de Publicidad': 2.5,      # Dato largo
            'Días de Transmisión': 1.0,       # Dato pequeño
            'Fecha de Pago': 2.8,             # Dato largo (fecha con milisegundos)
            'Referencia de Pago': 2.5,        # Dato largo (números grandes)
            'Estado de Pago': 1.2             # Dato pequeño
        }

        # Suma total de los ratios
        total_ratio = sum(column_width_ratios.get(col, 1.0) for col in column_names)

        # Calcular el ancho de cada columna basado en el total disponible
        column_widths = [
            (column_width_ratios.get(col, 1.0) / total_ratio) * total_width  # Total width ya incluye el espacio sin márgenes
            for col in column_names
        ]

        return column_widths


    def draw_row_borders(self, pdf_canvas, x, y, column_widths, row_height):
        """
        Dibujar las líneas horizontales y verticales para crear celdas en cada fila.
        """
        # Dibujar la línea inferior de la fila actual
        pdf_canvas.line(x, y, x + sum(column_widths), y)

        # Dibujar las líneas verticales para cada celda
        for i in range(len(column_widths) + 1):
            pdf_canvas.line(x + sum(column_widths[:i]), y, x + sum(column_widths[:i]), y + row_height)

        # Dibujar la línea superior (solo es necesario si es la fila de encabezado)
        pdf_canvas.line(x, y + row_height, x + sum(column_widths), y + row_height)

    def is_binary(self):
        return True
