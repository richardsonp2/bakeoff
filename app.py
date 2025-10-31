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

df = pd.read_csv(DATAFILE)

# ------------------------------ MODE DETECTION ------------------------------
query_params = st.query_params
mode = query_params.get("mode", ["vote"])[0]

# ------------------------------ VOTING MODE ------------------------------
if mode == "vote":
    st.title("🍰 Bakeoff voting")

    # 1) make sure we have a place to store what THIS user has voted on
    if "voted_bakes" not in st.session_state:
        st.session_state.voted_bakes = []

    # 2) compute remaining bakes for THIS user
    remaining_bakes = [b for b in BAKES if b not in st.session_state.voted_bakes]

    # 3) if no bakes left → show finished screen
    if len(remaining_bakes) == 0:
        st.success("You’ve voted on everything — thanks for judging! 🎉")
        st.stop()

    # 4) normal voting form
    name = st.text_input("Your name (or anonymise)", "")
    bake = st.selectbox("Choose bake", remaining_bakes)
    taste = st.slider("Taste (1–10)", 1, 10, 8)
    texture = st.slider("Texture (1–10)", 1, 10, 8)
    appearance = st.slider("Appearance (1–10)", 1, 10, 8)

    if st.button("Submit vote"):
        # append to CSV
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

        # mark this bake as voted for THIS session
        st.session_state.voted_bakes.append(bake)

        st.success(f"Vote for {bake} submitted ✅")

        # rerun so the selectbox refreshes and that bake disappears
        st.rerun()

# ------------------------------ ADMIN MODE ------------------------------
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
        st.dataframe(agg)
        st.subheader("🥇 Winner")
        st.write(agg.head(1))
