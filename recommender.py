"""Explainable recommenders.

1. Popularity-based: highest average rating among movies with enough ratings.
2. Similarity-based (item-item): two movies are similar when the people who rated both
   tended to rate them above/below their own personal average in the same direction
   (adjusted cosine similarity, computed with NumPy).

Every result carries a plain-language `reason`. Reasons only mention the requesting
person's OWN ratings and aggregate numbers, never another user's ratings.
"""
import numpy as np
import pandas as pd

from config import MIN_OVERLAP, MIN_RATING_COUNT, MIN_USER_RATINGS


def popular(stats: pd.DataFrame, n: int = 5, exclude_ids=()) -> list[dict]:
    df = stats[stats["qualifies"] & ~stats["movie_id"].isin(list(exclude_ids))]
    df = df.sort_values(["avg_rating", "rating_count"], ascending=False).head(n)
    out = []
    for row in df.itertuples():
        out.append({
            "movie_id": int(row.movie_id), "title": row.title, "genre": row.genre,
            "release_year": int(row.release_year), "avg_rating": float(row.avg_rating),
            "rating_count": int(row.rating_count), "method": "popularity",
            "reason": (f"Average rating {row.avg_rating:.2f} from {row.rating_count} ratings "
                       f"(listed only with at least {MIN_RATING_COUNT} ratings)."),
        })
    return out


def _similarity(r: pd.DataFrame):
    """Return (similarity DataFrame, overlap DataFrame), both indexed by movie_id."""
    pivot = r.pivot_table(index="user_id", columns="movie_id", values="rating")
    centered = pivot.sub(pivot.mean(axis=1), axis=0)      # remove each user's own average
    z = centered.fillna(0).to_numpy()
    num = z.T @ z
    norms = np.sqrt((z ** 2).sum(axis=0))
    denom = np.outer(norms, norms)
    sim = np.divide(num, denom, out=np.zeros_like(num), where=denom > 0)
    mask = pivot.notna().to_numpy(dtype=float)
    overlap = mask.T @ mask                                # users who rated both movies
    sim[overlap < MIN_OVERLAP] = 0.0
    np.fill_diagonal(sim, 0.0)
    idx = pivot.columns
    return pd.DataFrame(sim, index=idx, columns=idx), pd.DataFrame(overlap, index=idx, columns=idx)


def similar_movies(r: pd.DataFrame, stats: pd.DataFrame, movie_id: int, n: int = 5) -> list[dict]:
    if r.empty or movie_id not in set(r["movie_id"]):
        return []
    sim, overlap = _similarity(r)
    if movie_id not in sim.index:
        return []
    row = sim.loc[movie_id]
    row = row[row > 0].sort_values(ascending=False)
    info = stats.set_index("movie_id")
    out = []
    for other_id, score in row.items():
        meta = info.loc[other_id]
        if not meta["qualifies"]:
            continue
        out.append({
            "movie_id": int(other_id), "title": meta["title"], "genre": meta["genre"],
            "release_year": int(meta["release_year"]), "avg_rating": float(meta["avg_rating"]),
            "rating_count": int(meta["rating_count"]), "similarity": round(float(score), 2),
            "method": "similarity",
            "reason": (f"Similarity {score:.2f}: the {int(overlap.loc[movie_id, other_id])} people "
                       f"who rated both tended to score them the same way."),
        })
        if len(out) >= n:
            break
    return out


def recommend_for_user(r: pd.DataFrame, stats: pd.DataFrame, user_id: int, n: int = 5):
    """Return (recommendations, note). Falls back to popularity when there is too little data."""
    mine = r[r["user_id"] == user_id]
    already = set(mine["movie_id"])
    if len(mine) < MIN_USER_RATINGS:
        note = (f"Rate at least {MIN_USER_RATINGS} movies to unlock personalised "
                f"recommendations. Showing popular movies you have not rated.")
        return popular(stats, n, already), note

    sim, _ = _similarity(r)
    info = stats.set_index("movie_id")
    titles = info["title"]
    my_ratings = mine.set_index("movie_id")["rating"]
    rated_in_matrix = [mid for mid in my_ratings.index if mid in sim.columns]

    results = []
    for cand, meta in info[info["qualifies"]].iterrows():
        if cand in already or cand not in sim.index:
            continue
        s = sim.loc[cand, rated_in_matrix]
        s = s[s > 0].sort_values(ascending=False).head(5)
        if s.empty:
            continue
        pred = float((s * my_ratings[s.index]).sum() / s.sum())
        top_id = (s * my_ratings[s.index]).idxmax()   # the rated movie that contributed most
        results.append({
            "movie_id": int(cand), "title": meta["title"], "genre": meta["genre"],
            "release_year": int(meta["release_year"]), "avg_rating": float(meta["avg_rating"]),
            "rating_count": int(meta["rating_count"]),
            "predicted_rating": round(min(pred, 5.0), 2), "method": "similarity",
            "reason": (f"You rated \"{titles[top_id]}\" {my_ratings[top_id]:g}, and people who "
                       f"rated both scored them alike (similarity {s[top_id]:.2f}). "
                       f"Predicted from {len(s)} of your rated movie(s)."),
        })
    results.sort(key=lambda d: (d["predicted_rating"], d["rating_count"]), reverse=True)
    results = results[:n]
    note = "Based on your own ratings and rating patterns across all users. A suggestion, not a guarantee."
    if len(results) < n:
        extra = popular(stats, n - len(results), already | {d["movie_id"] for d in results})
        results += extra
    return results, note
