import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

BAKES = ["Cookies", "Brownies", "Pie", "Cheesecake", "Flapjack"]
DATAFILE = Path("bakeoff_votes.csv")

# make sure file exists
if not DATAFILE.exists():
    df_init = pd.DataFrame(
        columns=["timestamp", "name", "bake", "taste", "texture", "appearance"]
    )
    df_init.to_csv(DATAFILE, index=False)

# always try to read current votes
df = pd.read_csv(DATAFILE)

# ------------------------------ MODE DETECTION ------------------------------
query_params = st.experimental_get_query_params()
mode = query_params.get("mode", ["vote"])[0]  # "vote", "admin", "entries"

# =====================================================================
# 1) VOTING MODE
# =====================================================================
if mode == "vote":
    st.title("🍰 Bakeoff voting")

    # per-user session store
    if "voted_bakes" not in st.session_state:
        st.session_state.voted_bakes = []

    remaining_bakes = [b for b in BAKES if b not in st.session_state.voted_bakes]

    if len(remaining_bakes) == 0:
        st.success("You’ve voted on everything — thanks for judging! 🎉")
        st.stop()

    name = st.text_input("Your name (or anonymise)", "")
    bake = st.selectbox("Choose bake", remaining_bakes)
    taste = st.slider("Taste (1–10)", 1, 10, 8)
    texture = st.slider("Texture (1–10)", 1, 10, 8)
    appearance = st.slider("Appearance (1–10)", 1, 10, 8)

    if st.button("Submit vote"):
        new_row = pd.DataFrame([{
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "name": name,
            "bake": bake,
            "taste": taste,
            "texture": texture,
            "appearance": appearance,
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATAFILE, index=False)

        st.session_state.voted_bakes.append(bake)

        st.success(f"Vote for {bake} submitted ✅")
        st.rerun()

# =====================================================================
# 2) ENTRIES MODE (pretty, public-friendly view)
# =====================================================================
elif mode == "entries":
    st.markdown(
        """
        <h1 style="text-align:center; font-weight:700; font-size:2.5rem; color:#5B3A1A;">
            🍪 Current Entries
        </h1>
        <p style="text-align:center; margin-bottom:2rem; color:#7B4B2A;">
            Here are the bakes in this round and how many people have judged them so far:
        </p>
        """,
        unsafe_allow_html=True
    )

    # count votes per bake
    if df.empty:
        counts = {b: 0 for b in BAKES}
    else:
        counts = df["bake"].value_counts().to_dict()
        for b in BAKES:
            counts.setdefault(b, 0)

    # cookie + chocolate palette
    cookie_bg = "#E6C199"     # warm cookie dough colour
    choc_text = "#4B2E05"     # dark chocolate brown
    choc_shadow = "rgba(75, 46, 5, 0.25)"

    cols = st.columns(3)
    for i, bake in enumerate(BAKES):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="
                    background-color: {cookie_bg};
                    color: {choc_text};
                    border-radius: 16px;
                    padding: 16px 16px 12px 16px;
                    margin-bottom: 16px;
                    box-shadow: 0 4px 10px {choc_shadow};
                    min-height: 110px;
                    text-align:center;
                ">
                    <h3 style="margin: 0 0 6px 0; color: {choc_text};">{bake}</h3>
                    <p style="margin: 0; color: {choc_text}; font-size: 0.9rem;">
                        Votes so far: <strong>{counts[bake]}</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.info("Scores are still hidden — this is just the participation tally 👀")

# =====================================================================
# 3) ADMIN MODE (full results)
# =====================================================================
else:
    st.title("📊 Bakeoff results")

    if df.empty:
        st.info("No votes yet.")
    else:
        agg = (
            df.groupby("bake")
              .agg(
                  n_votes=("bake", "count"),
                  taste_mean=("taste", "mean"),
                  texture_mean=("texture", "mean"),
                  appearance_mean=("appearance", "mean"),
              )
        )
        agg["overall_mean"] = (
            agg["taste_mean"] + agg["texture_mean"] + agg["appearance_mean"]
        ) / 3
        agg = agg.sort_values("overall_mean", ascending=False)

        st.subheader("All scores")
        st.dataframe(agg, use_container_width=True)

        st.subheader("🥇 Winner (so far)")
        st.write(agg.head(1))
