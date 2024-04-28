from evidence_group.serializers import EvidenceGroupSerializer
from rest_framework import views, generics, authentication, permissions
from rest_framework import views
from rest_framework.response import Response

from core import models
from rest_framework import status
from django.db import connection


class EvidenceAnalyticsView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def query(self, group_id, division_id, onwers_id, evidences_id):

        onwers_id = [str(ele) for ele in onwers_id] 
        evidences_id = [str(ele) for ele in evidences_id] 

        division_str = ""
        if division_id != None:            
            division_str = f"AND profile.division_id = {division_id}"
        
        owners_str = ""
        if len(onwers_id) > 0:
            ids = ', '.join(onwers_id)
            owners_str = f"e.owner_id IN ({ids})"

        evidences_str = ""
        if len(evidences_id) > 0:
            ids = ', '.join(evidences_id)
            evidences_str = f"e.id IN ({ids})"

        ownership_cond = ""
        if len(owners_str) > 0 and len(evidences_str):
            ownership_cond = f"AND ( {owners_str} or {evidences_str} )"
        elif len(owners_str) > 0:
            ownership_cond = f"AND {owners_str}"
        elif len(evidences_str) > 0:
            ownership_cond = f"AND {evidences_str}"
            
        with connection.cursor() as cursor:
            query = f"""SELECT 
                            --eg.id AS group_id,
                            status.id AS status_id,
                            STRING_AGG(DISTINCT status.name, '') AS status,
                            STRING_AGG(DISTINCT status.color, '') AS color,
                            count(e.id)
                        FROM 
                            core_evidence AS e
                        LEFT JOIN
                            core_evidencegroup AS eg 
                                ON eg.id = e.group_id
                        LEFT JOIN
                            core_evidencestatus AS status 
                                ON status.id = e.status_id
                        LEFT JOIN
                            core_evidencestage AS stage 
                                ON stage.id = status.stage_id
                        LEFT JOIN
                            core_user AS u 
                                ON u.id = e.owner_id
                        LEFT JOIN
                            core_profile AS profile 
                                ON profile.user_id = u.id
                        WHERE
                            eg.id = {group_id}
                            {division_str}
                            {ownership_cond}
                        GROUP BY
                            eg.id,
                            status.id
                        """

            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return data
        pass

    def get(self, request):

        if not (self.request.user.has_perm('core.manage_evidence') or self.request.user.has_perm('core.work_evidence') or self.request.user.has_perm('core.view_evidence')):
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        owners = []
        evidences = []
        division_id = None
        
        if self.request.user.has_perm('core.manage_evidence'): 
            division_id = self.request.user.profile.division.id
        elif self.request.user.has_perm('core.work_evidence'):
            owners.append(request.user)
            # Signers
            signers = models.EvidenceSignature.objects.filter(user=self.request.user)
            for v in signers:
                evidences.append(v.evidence.id)

            # Authorizers
            authorizers = models.EvidenceAuth.objects.filter(user=self.request.user)
            for v in authorizers:
                evidences.append(v.evidence.id)
   
        onwers_id = []
        for owner in owners:
            onwers_id.append(owner.id)
        
        evidences_id = []
        for evidence in evidences:
            evidences_id.append(evidence.id)

        data = []
        groups = models.EvidenceGroup.objects.all()
        for group in groups:
            group_data = self.query(group.id, division_id, onwers_id, evidences_id)
            s = EvidenceGroupSerializer(group)
            data.append({
                "group": s.data,
                "analytics": group_data
            })
        
        return Response(data)
