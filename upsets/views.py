from upsets.models import UpsetTreeNode, Player, TwitterTag, TreeContainer
from upsets.serializers import UpsetTreeNodeSerializer, PlayerSerializer
from django.http import Http404, HttpResponseBadRequest
from django.db.models import BooleanField, Case, Value, When
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
import json

from logging import getLogger
logger = getLogger('data_processing')


class UpsetPath(APIView):
    """
    Retrieve the upset root path given a player id
    """

    def get(self, request, id, format=None):
        # GET parameters are always strings.
        offline_only_str = request.GET.get('offline_only', 'False')
        if offline_only_str == 'False':
            offline_only = False
        elif offline_only_str == 'True':
            offline_only = True
        else:
            # Use the same format as DRF errors
            return HttpResponseBadRequest(
                json.dumps({
                    'detail': 'GET parameter offline_only should be either ' +
                              'not defined, True, or False.'
                    }),
                content_type="application/json")
        # offline_only correctly defined
        try:
            player = Player.objects.get(id=id)
            try:
                container = TreeContainer.objects \
                    .filter(ready=True) \
                    .filter(offline_only=offline_only) \
                    .order_by('-update_date') \
                    .first()
                upset_node = UpsetTreeNode.objects \
                    .filter(tree_container=container) \
                    .get(player=player)
            except UpsetTreeNode.DoesNotExist:
                return Response(
                    {'player_tag': player.tag,
                     'offline_only': offline_only,
                     'path_exist': False})
        except Player.DoesNotExist:
            raise Http404

        upset_root_path = upset_node.get_root_path()
        serializer = UpsetTreeNodeSerializer(upset_root_path, many=True)
        return Response(
            {'player_tag': player.tag,
             'offline_only': offline_only,
             'path_exist': True,
             'path': serializer.data})


class PlayerSearch(ListAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        """
        Restricts the returned players by filtering tags against the `term`
        query parameter in the URL.
        """
        searchterm = self.request.query_params.get('term', None)
        if searchterm:
            queryset = Player.objects \
                .filter(tag__unaccent__icontains=searchterm) \
                .annotate(
                    is_start=Case(
                        When(tag__unaccent__istartswith=searchterm,
                             then=Value(True)),
                        default=False,
                        output_field=BooleanField()),
                    is_exact=Case(
                        When(tag__unaccent__iexact=searchterm,
                             then=Value(True)),
                        default=False,
                        output_field=BooleanField())) \
                .select_related('last_tournament') \
                .order_by('-is_exact', '-is_start', '-played_sets_count')
            return queryset[:20]
        else:
            message = \
                "Url should contain a non empty 'term' query string parameter."
            raise ParseError(detail=message)


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
                valid = twittertag.is_valid()
                if valid:
                    return Response(
                        {'player_id': player.id,
                         'twitter_tag': twittertag.tag})
        except Player.DoesNotExist:
            raise Http404
        return Response(
            {'player_id': player.id,
             'twitter_tag': None})
