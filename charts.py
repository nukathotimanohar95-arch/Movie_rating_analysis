"""Matplotlib charts returned as PNG bytes."""
import io

import matplotlib
matplotlib.use("Agg")  # no GUI needed on a server
import matplotlib.pyplot as plt  # noqa: E402

ACCENT = "#0f766e"
INK = "#1f2933"


def _png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def _empty(title: str) -> bytes:
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.text(0.5, 0.5, "No data yet", ha="center", va="center", color=INK)
    ax.set_axis_off()
    ax.set_title(title)
    return _png(fig)


def _style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=INK)


def genre_chart(g) -> bytes:
    g = g[g["total_ratings"] > 0].sort_values("avg_rating")
    if g.empty:
        return _empty("Average rating by genre")
    fig, ax = plt.subplots(figsize=(7, 0.55 * len(g) + 1.4))
    bars = ax.barh(g["genre"], g["avg_rating"], color=ACCENT)
    for bar, (_, row) in zip(bars, g.iterrows()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{row["avg_rating"]:.2f}  ({row["total_ratings"]} ratings)',
                va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 5.8)
    ax.set_xlabel("Average rating (0.5 - 5)")
    ax.set_title("Average rating by genre", loc="left", color=INK)
    _style(ax)
    return _png(fig)


def distribution_chart(d) -> bytes:
    if d["count"].sum() == 0:
        return _empty("Rating distribution")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    bars = ax.bar([f"{v:g}" for v in d["rating"]], d["count"], color=ACCENT)
    for bar, c in zip(bars, d["count"]):
        if c:
            ax.text(bar.get_x() + bar.get_width() / 2, c, str(c), ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of ratings")
    ax.set_title("Rating distribution", loc="left", color=INK)
    _style(ax)
    return _png(fig)


def top_chart(top) -> bytes:
    if top.empty:
        return _empty("Top-rated movies")
    t = top.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 0.5 * len(t) + 1.4))
    bars = ax.barh(t["title"], t["avg_rating"], color=ACCENT)
    for bar, (_, row) in zip(bars, t.iterrows()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{row["avg_rating"]:.2f}  (n={row["rating_count"]})', va="center", fontsize=9)
    ax.set_xlim(0, 5.8)
    ax.set_xlabel("Average rating")
    ax.set_title("Top-rated movies", loc="left", color=INK)
    _style(ax)
    return _png(fig)
