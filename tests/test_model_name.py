from tortoise.models import Model


class TM(Model):
    pass


assert TM.__name__ == "TM"
