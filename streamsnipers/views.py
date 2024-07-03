from django.shortcuts import render
from django.views import View
from .models import Score


class StreamSniperRanking(View):

    def get(self, request):

        scores = Score.objects.all()
        ranking = {}
        for score in scores:
            name = (
                score.streamsniper.riotIdGameName
                + " #"
                + score.streamsniper.riotIdTagline
            )
            ranking[name] = (
                score.win_with_quin
                + score.loss_against_quin
                - score.win_against_quin
                - score.loss_with_quin
            )
        sortedranking = sorted(ranking.items(), key=lambda x: x[1])
        griefers = [griefer[0] for griefer in sortedranking[:5]]
        carries = [carry[0] for carry in list(reversed(sortedranking[-5:]))]
        context = {"carries": carries, "griefers": griefers}

        return render(request, "ranking.html", context=context)
