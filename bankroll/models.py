from django.db import models

FORMAT = (
    ("homegame", "Home game"),
    ("casino", "Casino"),
)

TYPE = (
    ("poker", "Poker"),
    ("blackjack", "Blackjack"),
)

class Session(models.Model):
    host = models.CharField(max_length=100)                        # playground or homegame host
    format = models.CharField(max_length=100, choices=FORMAT)      # homegame or casino
    type = models.CharField(max_length=100, null=True, blank=True) # poker or blackjack or roulette etc
    stakes = models.CharField(max_length=100)                      # 1/2$ or 2/5$ or 5/10$ etc

    date = models.DateTimeField(auto_now_add=True)
    session_start = models.DateTimeField()
    session_end = models.DateTimeField()

    buyin = models.PositiveIntegerField(default=0)
    buyout = models.PositiveIntegerField(default=0)

    @property
    def profit(self):
        return self.buyout - self.buyin

    def __str__(self):
        formatted_date = self.date.strftime('%Y-%m-%d') if self.date else "Unsaved Session"
        return f"{self.get_format_display()} on {formatted_date} at {self.host} with profit of {self.profit}$"
