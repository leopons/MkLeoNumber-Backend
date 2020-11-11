from upsets.models import UpsetTreeNode, Player
from upsets.serializers import UpsetTreeNodeSerializer
from django.http import Http404
from rest_framework.views import APIView
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
