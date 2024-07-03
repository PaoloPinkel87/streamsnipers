from django.shortcuts import render
from django.views import View


class StreamSniperRanking(View):

    def get(self, request):

        context = {"title": "test"}

        return render(request, "ranking.html", context=context)
