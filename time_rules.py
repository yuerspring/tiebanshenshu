"""Civil clock coordinates kept separate from the inherited late-Zi calendar rule."""
import datetime as dt


def shichen_start(civil):
    midnight = civil.replace(hour=0, minute=0, second=0, microsecond=0)
    if civil.hour == 0:
        return midnight - dt.timedelta(hours=1)
    return midnight + dt.timedelta(hours=((civil.hour - 1) // 2) * 2 + 1)


def clock_coordinates(civil):
    elapsed = int((civil - shichen_start(civil)).total_seconds() // 60)
    return {'quarter': elapsed // 15 + 1, 'minute_in_shichen': elapsed,
            'minute_in_quarter': elapsed % 15}


def calendar_birth_time(civil):
    # Preserve the existing V2 day-boundary convention, not a new school rule.
    if civil.hour == 23:
        return (civil + dt.timedelta(days=1)).replace(hour=0)
    return civil
