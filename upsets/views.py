from upsets.models import UpsetTreeNode, Player, TwitterTag
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
            queryset = queryset.filter(tag__unaccent__icontains=searchterm) \
                               .select_related('last_tournament') \
                               .order_by('-played_sets_count')
        return queryset[:20]


class PlayerTwitterTag(APIView):
    """
    Get a valid twitter tag for a given player id.

    We made this a different endpoint than the upsetpath. We could include this
    in the serializer of the Player but it would increase the upsetpath
    response time significatively for an enduser (possibly mutiple synchronous
    calls to twitter) so we prefer to keep this separated and make
    asynchronous calls from the front end
    """
    def get(self, request, id, format=None):
        try:
            player = Player.objects.get(id=id)
            twittertags_candidates = TwitterTag.objects.filter(
                player=player, obsolete=False)
            for twittertag in twittertags_candidates:
                valid = twittertag.check_validity()
                if valid:
                    return Response(
                        {'player_id': player.id,
                         'twitter_tag': twittertag.tag})
        except Player.DoesNotExist:
            raise Http404
        return Response(
            {'player_id': player.id,
             'twitter_tag': None})
