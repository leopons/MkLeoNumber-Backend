from upsets.models import UpsetTreeNode, Player
from upsets.serializers import UpsetTreeNodeSerializer, PlayerSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class UpsetPath(APIView):
    """
    Retrieve the upset root path given a player id
    """

    def get(self, request, id, format=None):
        try:
            player = Player.objects.get(id=id)
            try:
                upset_node = UpsetTreeNode.objects.get(player=player)
            except UpsetTreeNode.DoesNotExist:
                return Response(
                    {'player_tag': player.tag, 'path_exist': False})
        except Player.DoesNotExist:
            raise Http404

        upset_root_path = upset_node.get_root_path()
        serializer = UpsetTreeNodeSerializer(upset_root_path, many=True)
        return Response(
            {'player_tag': player.tag,
             'path_exist': True,
             'path': serializer.data})


class PlayerSearch(ListAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        """
        Restricts the returned players by filtering tags against the `term`
        query parameter in the URL.
        """
        queryset = Player.objects.all()
        searchterm = self.request.query_params.get('term', None)
        if searchterm is not None:
            queryset = queryset.filter(tag__unaccent__icontains=searchterm)
        return queryset[:20]
