from rest_framework import serializers
from upsets.models import UpsetTreeNode, Set, Tournament


class TournamentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tournament
        fields = ['name', 'start_date']


class SetSerializer(serializers.ModelSerializer):

    tournament = TournamentSerializer()
    winner = serializers.SlugRelatedField(slug_field='tag', read_only=True)
    looser = serializers.SlugRelatedField(slug_field='tag', read_only=True)

    class Meta:
        model = Set
        fields = ['tournament', 'winner', 'looser', 'winner_score',
                  'looser_score', 'round_name', 'best_of']


class UpsetTreeNodeSerializer(serializers.ModelSerializer):
    upset = SetSerializer()

    class Meta:
        model = UpsetTreeNode
        fields = ['node_depth', 'upset']
