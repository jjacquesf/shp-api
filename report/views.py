
import os
import json

from platform import python_version
from django.db import connection

from report.serializers import EvidenceReportSerializer
from rest_framework import views
from rest_framework.response import Response

from core import models

# @extend_schema(tags=['User management'])
class ReportView(views.APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated, UserPermission]

    def get(self, request):
        serializer = EvidenceReportSerializer(data={
            "group_id": 2,
            "type_id": 1,
            "cf_ids": [2,3]
        })
        serializer.is_valid(raise_exception=True)

        cf_ids = serializer.validated_data.get("cf_ids")

        fields = []
        subqueries = []
        group_bys = []
        for idx, attr_id in enumerate(cf_ids):
            fields.append(f"""
                    val{idx + 1}.value_text AS gf{idx + 1}""")
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

                query = f"""SELECT 
                                        eg.id AS group_id,
                                        et.id AS type_id,
                                        d.id AS division_id,
                                        {fields_str}
                                        STRING_AGG(DISTINCT eg.name, '') AS group_name,
                                        STRING_AGG(DISTINCT et.name, '') AS type_name,
                                        STRING_AGG(DISTINCT d.name, '') AS division_name,
                                        STRING_AGG(DISTINCT es.name, '') AS status_name,
                                        COUNT(eg.id) AS group_count,
                                        COUNT(et.id) AS type_count,
                                        COUNT(d.id) AS division_count,
                                        JSON_AGG(JSONB_BUILD_OBJECT(
                                            'id', e.id,
                                            'created_at', e.created_at,
                                            'updated_at', e.updated_at,
                                            'user', u.name,
                                            'job_position', p.job_position
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


                for r in data:
                    evidences = r.get("evidences")
                    print(r)
                    for e in evidences:
                        print(e)
                    print('======')
                    print('======')
                    print('======')

        return Response(serializer.data)