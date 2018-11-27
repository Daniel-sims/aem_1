from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from company.renderers import CompanyJSONRenderer
from company.serializers import CompanySerializer


class CreateCompanyAPIView(APIView):
    """
        Creates a company with an ID and a Name.
        Ideally this View should be Authenticated but I can't think of a smooth way
        of doing it.
    """

    permission_classes = (AllowAny,)
    renderer_classes = (CompanyJSONRenderer,)
    serializer_class = CompanySerializer

    def post(self, request):
        company = request.data.get('company', {})
        print(company)

        serializer = self.serializer_class(data=company)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
