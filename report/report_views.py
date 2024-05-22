
import os
import io
import datetime
import tempfile
import uuid
import zipfile
from platform import python_version
from django.db import connection
from django.http import FileResponse
from rest_framework.response import Response

from rest_framework import views, generics, authentication, permissions

from report.serializers import EvidenceReportSerializer
from rest_framework import views

from core import models

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle as PS
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status


class CustomImage(Image):
    """
    Override - to use inline image instead; inexplicable bug with non inline images
    """
    def draw(self):
        lazy = self._lazy
        if lazy>=2: self._lazy = 1
        self.canv.drawInlineImage(self.filename,
            getattr(self,'_offs_x',0),
            getattr(self,'_offs_y',0),
            self.drawWidth,
            self.drawHeight
        )
        if lazy>=2:
            self._img = None
            self._lazy = lazy

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
                             "Página %d de %d" % (self._pageNumber, page_count))

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
        subtitle = Paragraph('Reporte de estatus de evidencias', h2)
        

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
    
    def build(self, items, cf_ids):
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


            bolder = PS(name='bolder', fontSize=12, leading=14)
            normal = PS(name='normal', fontSize=10, leading=12)


            group_table_style = TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 10), 
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.white),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                ])

            # Need a place to store our table rows
            for i, item in items:

                table_group_data = []
                table_group_data.append([Paragraph('Grupo de evidencias', bolder), Paragraph('Tipo de evidencias', bolder)])
                table_group_data.append([item.get('group_name'), item.get('type_name')])

                group_data_table = Table(table_group_data, colWidths=[doc.width/2.0]*2, spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
                group_data_table.setStyle(group_table_style)
                elements.append(group_data_table)

                table_group_data = []
                table_group_data.append([Paragraph('División', bolder), Paragraph('', bolder)])
                table_group_data.append([item.get('division_name'), ''])

                group_data_table = Table(table_group_data, colWidths=[doc.width/2.0]*2, spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
                group_data_table.setStyle(group_table_style)
                elements.append(group_data_table)

                cf_id_count = len(cf_ids)
                if cf_id_count > 0:

                    table_group_data = []

                    table_group_data_headers = []
                    table_group_data_data = []
                    if cf_id_count == 1:
                        for j, cf_id in enumerate(cf_ids):
                            table_group_data_headers.append( Paragraph(item.get(f'attr{j + 1}_name'), bolder) )
                            table_group_data_data.append( Paragraph(item.get(f'gf{j + 1}'), bolder) )

                        table_group_data.append( table_group_data_headers )
                        table_group_data.append( table_group_data_data )

                        group_data_table = Table(table_group_data, colWidths=[doc.width/cf_id_count]*cf_id_count, spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
                        group_data_table.setStyle(group_table_style)
                        elements.append(group_data_table)


                table_data = []
                table_data.append(['Creado', 'Actualizado', 'Responsable', 'Puesto', 'Estatus'])
                for k, evidence in enumerate(item.get('evidences')):
                    # Add a row to the table
                    created_at = datetime.datetime.fromisoformat(evidence.get('created_at')).strftime("%d/%m/%Y")
                    updated_at = datetime.datetime.fromisoformat(evidence.get('updated_at')).strftime("%d/%m/%Y")
                    table_data.append([created_at, updated_at, evidence.get('user'), evidence.get('job_position'), evidence.get('status_name')])

                # Create the table
                data_table = Table(table_data, colWidths=[doc.width/5.0]*5, spaceBefore=doc.height*1/100, spaceAfter=doc.height*1/100)
                data_table.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 10), 
                                                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                                ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
                elements.append(data_table)

            elements.append(Spacer(1,2*inch))

            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                    canvasmaker=NumberedCanvas)
            
            buffer.seek(0)

            return buffer


class Excel:
    # def __init__(self, buffer):
    #     self.buffer = buffer

    def build(self, items, cf_ids):
        buffer = io.BytesIO()

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sample Sheet"

        # Add some data to the sheet.
        data = [
            ['Header1', 'Header2', 'Header3'],
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        for row in data:
            sheet.append(row)

        # Save the workbook to the BytesIO object
        
        # with tempfile.TemporaryDirectory() as temp_dir:
        #     name = f"{uuid.uuid4()}.xlsx"
        #     tmp_file = os.path.join(temp_dir, name)
        #     workbook.save(tmp_file)
        
        # tmp_file = "./tmpreport.xlsx"
        # workbook.save(tmp_file)

        workbook.save(buffer)

        # Rewind the buffer
        buffer.seek(0)
        # return tmp_file 
        return buffer

# @extend_schema(tags=['User management'])
class EvidenceReportView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def query(self, config):
        cf_ids = config.get("cf_ids")

        fields = []
        subqueries = []
        group_bys = []
        for idx, attr_id in enumerate(cf_ids):
            fields.append(f"""
                    val{idx + 1}.value_text AS gf{idx + 1},
                    STRING_AGG(DISTINCT attr{idx + 1}.name, '') AS attr{idx + 1}_name""")
            subqueries.append(f"""
                    LEFT JOIN
                        eav_value AS val{idx + 1}
                            ON e.id = val{idx + 1}.entity_id
                            AND val{idx + 1}.attribute_id = {attr_id}
                            AND val{idx + 1}.entity_ct_id = (
                                SELECT
                                    ct.id
                                FROM 
                                    django_content_type AS ct
                                WHERE
                                    ct.app_label = 'core'
                                    AND ct.model = 'evidence'
                                LIMIT 1
                            )
                    LEFT JOIN
                        eav_attribute AS attr{idx + 1}
                            ON attr{idx + 1}.id = val{idx + 1}.attribute_id
                """)
            group_bys.append(f"""
                             val{idx + 1}.value_text""")

        with connection.cursor() as cursor:
            fields_str = ''
            if(len(fields) > 0):
                fields_str = ','.join(fields) + ","

            group_bys_str = ''
            if(len(group_bys) > 0):
                group_bys_str = ',' + ','.join(group_bys)


            # to_char(e.created_at, 'YYYY-MM-DD"T"HH24:MI:SSOF'),
            # to_char(e.updated_at, 'YYYY-MM-DD"T"HH24:MI:SSOF'),
            query = f"""SELECT 
                                    eg.id AS group_id,
                                    et.id AS type_id,
                                    d.id AS division_id,
                                    {fields_str}
                                    STRING_AGG(DISTINCT eg.name, '') AS group_name,
                                    STRING_AGG(DISTINCT et.name, '') AS type_name,
                                    STRING_AGG(DISTINCT d.name, '') AS division_name,
                                    COUNT(eg.id) AS group_count,
                                    COUNT(et.id) AS type_count,
                                    COUNT(d.id) AS division_count,
                                    JSON_AGG(JSONB_BUILD_OBJECT(
                                        'id', e.id,
                                        'created_at', to_char(e.created_at, 'YYYY-MM-DD"T"HH24:MI'), --e.created_at,
                                        'updated_at', to_char(e.updated_at, 'YYYY-MM-DD"T"HH24:MI'), --e.updated_at,
                                        'user', u.name,
                                        'job_position', p.job_position,
                                        'status_name', es.name
                                    )) AS evidences
                                FROM 
                                    core_evidence AS e
                                LEFT JOIN
                                    core_evidencestatus AS es
                                    ON e.status_id = es.id
                                LEFT JOIN
                                    core_evidencetype AS et
                                    ON e.type_id = et.id
                                LEFT JOIN
                                    core_evidencegroup AS eg
                                    ON eg.id = et.group_id
                                LEFT JOIN
                                    core_user AS u
                                    ON e.owner_id = u.id
                                LEFT JOIN
                                    core_profile AS p
                                    ON u.id = p.user_id
                                LEFT JOIN
                                    core_division AS d
                                    ON p.division_id = d.id
                                {''.join(subqueries)}
                                GROUP BY
                                    eg.id,
                                    et.id,
                                    d.id
                                    {group_bys_str}
                                """
            
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return enumerate(data)
    
    def post(self, request):
        serializer = EvidenceReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = self.query(serializer.data)

        format = serializer.validated_data.get("format")
        cf_ids = serializer.validated_data.get("cf_ids")

        if format == None or format == "pdf":
            buf = io.BytesIO()
            pdf = Print(buf, 'Letter')
            buf = pdf.build(data, cf_ids)

            return FileResponse(buf, as_attachment=True, filename="report.pdf")
        else:
            
            excel = Excel()
            buf = excel.build(data, cf_ids)

            # return FileResponse(buf, as_attachment=True, filename="report.xlsx")

            # if not os.path.exists(file_path):
            #     return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

            return FileResponse(buf, as_attachment=True, filename="report.xlsx")
            # response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        
        # return response
        
        # buf = io.BytesIO()
        # pdf = Print(buf, 'Letter')
        # buf = pdf.build(data, cf_ids)

        # return FileResponse(buf, as_attachment=True, filename="report.pdf")