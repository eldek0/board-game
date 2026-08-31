"""Player colors derived from the seed: pure, deterministic, no drawing involved."""
import colorsys


def player_colors(count: int, seed: int) -> tuple[tuple[int, int, int], ...]:
    """One distinguishable RGB color per player, spread evenly around the hue circle.

    The seed only picks where the circle starts, so the colors are as far apart as
    the player count allows and the same seed always yields the same palette.
    """
    offset = (seed % 360) / 360

    return tuple(
        tuple(round(c * 255)
              for c in colorsys.hsv_to_rgb((offset + i / count) % 1.0, 0.85, 0.95))
        for i in range(count)
    )
