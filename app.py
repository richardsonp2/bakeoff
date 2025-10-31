import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

st.set_page_config("Bakeoff", layout="centered")

BAKES = ["Cookies", "Brownies", "Pie", "Cheesecake", "Flapjack"]
DATAFILE = Path("bakeoff_votes.csv")

# make sure file exists
if not DATAFILE.exists():
    df = pd.DataFrame(columns=["timestamp", "name", "bake", "taste", "texture", "appearance"])
    df.to_csv(DATAFILE, index=False)

# read current data
df = pd.read_csv(DATAFILE)

# ?mode=vote or ?mode=admin
query_params = st.query_params
mode = query_params.get("mode", ["vote"])[0]  # default vote

if mode == "vote":
    st.title("🍰 Bakeoff voting")
    name = st.text_input("Your name (or anonymise)", "")
    bake = st.selectbox("Choose bake", BAKES)
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
        st.success("Vote submitted ✅")
        st.rerun()

else:  # admin
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
        agg["overall_mean"] = (agg["taste_mean"] + agg["texture_mean"] + agg["appearance_mean"]) / 3
        agg = agg.sort_values("overall_mean", ascending=False)
        st.dataframe(agg)
        st.subheader("🥇 Winner")
        st.write(agg.head(1))
