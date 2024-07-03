from django.db import models

# Create your models here.


class StreamSniper(models.Model):

    riotIdGameName = models.CharField(max_length=255)
    riotIdTagline = models.CharField(max_length=255)

    class Meta:
        unique_together = ["riotIdGameName", "riotIdTagline"]


class Score(models.Model):

    streamsniper = models.ForeignKey(StreamSniper, on_delete=models.CASCADE)
    win_with_quin = models.PositiveSmallIntegerField(default=0)
    loss_with_quin = models.PositiveSmallIntegerField(default=0)
    win_against_quin = models.PositiveSmallIntegerField(default=0)
    loss_against_quin = models.PositiveSmallIntegerField(default=0)
    total_games = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ["streamsniper"]
