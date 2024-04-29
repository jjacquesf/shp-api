
import os
import io
import datetime

from evidence.serializers import EvidenceSerializer
from evidence_group.serializers import EvidenceGroupSerializer
from report.report_views import NumberedCanvas
from rest_framework import views, generics, authentication, permissions
from rest_framework import views
from rest_framework.response import Response

from core import models
from rest_framework import status
from django.db import connection

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle as PS
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from django.http import FileResponse

class Print:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        h1 = PS(name='h1', fontSize=18, leading=20, alignment=TA_CENTER)
        h2 = PS(name='h2', fontSize=14, leading=16, alignment=TA_CENTER)
        title = Paragraph('Secretaría de la Hacienda Pública', h1)
        subtitle = Paragraph('Detalle de entregable', h2)
        

        w, h = title.wrap(doc.width, doc.topMargin)
        title.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        w2, h2 = subtitle.wrap(doc.width, doc.topMargin)
        subtitle.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h - (h2*1.5))

        logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/logo.png')
        image = Image(logo)
        image.drawOn(canvas, 400, h - 400)

        # Footer
        footer = Paragraph('', styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()
    
    def build(self, instance):
            
            serializer = EvidenceSerializer(instance)

            buffer = self.buffer
            doc = SimpleDocTemplate(buffer,
                                    rightMargin=inch/4,
                                    leftMargin=inch/4,
                                    topMargin=inch/2,
                                    bottomMargin=inch/4,
                                    pagesize=self.pagesize)

            # Our container for 'Flowable' objects
            elements = []

            # A large collection of style sheets pre-made for us
            styles = getSampleStyleSheet()
            styles.add(PS(name='PStyle'))

            # # Draw things on the PDF. Here's where the PDF generation happens.
            # # See the ReportLab documentation for the full list of functionality.
            # elements.append(Paragraph('My User Names', styles['PStyle']))


            elements.append(Spacer(1,0.5*inch))

            printed_at = PS(name='topright', fontSize=10, alignment=TA_RIGHT)
            today = datetime.datetime.now()
            elements.append(Paragraph('Fecha de impresión', printed_at))
            elements.append(Paragraph(f"{today.strftime('%d/%m/%Y %H:%M hrs')}", printed_at))
            elements.append(Spacer(1,0.1*inch))

            elements.append(Paragraph(f"Versión: {instance.version}", printed_at))

            table_style = TableStyle([
                    ('SPAN', (0, 0), (-1, 0)),

                    ('FONTSIZE', (0, 0), (1, 0), 12), 
                    ('LEADING', (0, 0), (1, 0), 15), 


                    ('LINEBELOW', (1, 1), (1, -1), 0, colors.black),
                    ('LINEBELOW', (3, 1), (3, -1), 0, colors.black),
                ])


            created_at = instance.created_at.strftime("%d/%m/%Y")
            updated_at = instance.updated_at.strftime("%d/%m/%Y")

            table_data = []
            table_data.append(['Acerca del entregable'])
            table_data.append(['Grupo', instance.group.name, 'Tipo', instance.type.name])
            table_data.append(['Estatus', instance.status.name, 'División', instance.owner.profile.division.name])
            table_data.append(['Creación', created_at, 'Actualizado', updated_at])
            
            
            data_table = Table(table_data, colWidths=[doc.width*12/100, doc.width*38/100]*2, spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
            data_table.setStyle(table_style)
            elements.append(data_table)


            elements.append(Spacer(1,0.1*inch))

            table_data = []
            table_data.append(['Hallazgos en el documento'])
            data_table = Table(table_data, colWidths=[doc.width], spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
            data_table.setStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTSIZE', (0, 0), (1, 0), 12), 
                ('LEADING', (0, 0), (1, 0), 15), 
            ])
            elements.append(data_table)


            findings = serializer.data.get('quality_controls')
            table_data = []
            if(len(findings) > 0):

                for finding in findings:
                    subtable_data = []
                    subtable_data.append(['Fecha', 'Reporta', 'Tipo', 'Estatus'])

                    created_at = datetime.datetime.fromisoformat(finding.get('created_at')).strftime("%d/%m/%Y")
                    status = 'Pendiente'
                    if finding.get('status') != 'PEN':
                        status = 'Completado'
                        
                    subtable_data.append([created_at, finding.get('user').get('name'), finding.get('quality_control').get('name'), status])
                    subtable_data.append(['Observaciones'])
                    subtable_data.append([finding.get('comments')])

                table_style = TableStyle([
                        ('FONTSIZE', (0, 0), (-1, -1), 10), 
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ('SPAN', (0, 2), (-1, 2)),
                        ('SPAN', (0, 3), (-1, 3)),
                    ])

                data_table = Table(subtable_data, colWidths=[doc.width/4]*4, spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
                data_table.setStyle(table_style)
                elements.append(data_table)
            else:
                table_data.append(['No hay hallazgos registrados'])
                data_table = Table(table_data, colWidths=[doc.width], spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)

                elements.append(data_table)

            elements.append(Spacer(1,0.1*inch))





            elements.append(Spacer(1,2*inch))

            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                    canvasmaker=NumberedCanvas)
            
            buffer.seek(0)

            return buffer



class EvidenceExportView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request, pk):

        if not (self.request.user.has_perm('core.manage_evidence') or self.request.user.has_perm('core.work_evidence') or self.request.user.has_perm('core.view_evidence')):
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)
        
        instance = models.Evidence.objects.get(id=pk)

        buf = io.BytesIO()

        print = Print(buf, 'Letter')
        buf = print.build(instance)

        return FileResponse(buf, as_attachment=True, filename="report.pdf")