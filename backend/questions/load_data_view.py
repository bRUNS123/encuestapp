from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.core.management import call_command
from io import StringIO


@api_view(['POST'])
@permission_classes([IsAdminUser])
def load_personal_questions_view(request):
    """
    Temporary endpoint to load Personal questions into database.
    Only accessible by admin users.
    """
    try:
        # Capture command output
        out = StringIO()
        call_command('load_personal_questions', stdout=out)
        output = out.getvalue()
        
        return Response({
            'success': True,
            'message': 'Personal questions loaded successfully',
            'output': output
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
