import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Rozterki małżeńskie", layout="wide", page_icon="💔")

# ---------------------------------------------------------------------------
# STYL / TŁO Z FALAMI (SVG jako dekoracja rogów, tak jak na zdjęciu)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Tło aplikacji */
    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(91,155,213,0.18), transparent 35%),
            radial-gradient(circle at 100% 0%, rgba(237,125,49,0.18), transparent 35%),
            radial-gradient(circle at 0% 100%, rgba(112,173,71,0.15), transparent 35%),
            radial-gradient(circle at 100% 100%, rgba(155,89,182,0.18), transparent 35%),
            #fbfbfd;
    }

    /* Nagłówek */
    .app-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 600;
        color: #2c2c2c;
        margin-bottom: 0.2rem;
    }
    .app-sub {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    /* Karty wyników */
    .ev-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        height: 100%;
    }
    .ev-card.best {
        border: 2px solid #70AD47;
        box-shadow: 0 8px 24px rgba(112,173,71,0.25);
    }
    .ev-label { color:#555; font-size: 0.95rem; margin-bottom: 0.35rem; }
    .ev-value { font-size: 2rem; font-weight: 700; color: #222; margin:0; }
    .ev-badge {
        display:inline-block; margin-top:.4rem; padding:.15rem .6rem;
        background:#70AD47; color:white; border-radius:999px; font-size:.75rem;
    }

    section[data-testid="stSidebar"] { display:none; }

    h3 { text-align:center; margin-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-title">Rozterki małżeńskie 💔</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">UWAGA: gra na dwa fronty redukuje szanse o 80% na nową '
    '(np. 50% → 50×0,2 = 10%)</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# WEJŚCIA UŻYTKOWNIKA
# ---------------------------------------------------------------------------
st.markdown("### Prawdopodobieństwo")
col1, col2, col3 = st.columns(3)
with col1:
    p_better = st.slider("Nowa lepsza", 0, 100, 50, format="%d%%") / 100
with col2:
    p_want = st.slider("Udany atak na serce nowej", 0, 100, 50, format="%d%%") / 100
with col3:
    p_discover = st.slider("Obecna dowie się i zrywa", 0, 100, 30, format="%d%%") / 100

st.markdown("### Wartości")
col4, col5, col6, col7 = st.columns(4)
with col4:
    V_stay = st.slider("Obecny związek", -100, 100, 20)
with col5:
    V_alone = st.slider("Samotność", -100, 100, -12)
with col6:
    V_better = st.slider("Nowy związek gdy lepsza", -100, 100, 70)
with col7:
    V_worse = st.slider("Nowa gdy gorsza", -100, 100, -50)

st.divider()

# ---------------------------------------------------------------------------
# LOGIKA MODELU
# ---------------------------------------------------------------------------
TWO_FRONTS_MULTIPLIER = 0.2
p_want_two_fronts = p_want * TWO_FRONTS_MULTIPLIER

leaves_1 = [
    {"Strategia": "1. Pozostaje wierny", "Gałąź": "Zostaje z obecną",
     "Prawdopodobieństwo": 1.0, "Wartość": V_stay},
]
EV1 = V_stay

leaves_2 = [
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa chce, okazuje się lepsza",
     "Prawdopodobieństwo": p_want * p_better, "Wartość": V_better},
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa chce, okazuje się gorsza",
     "Prawdopodobieństwo": p_want * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa nie chce – zostaje sam",
     "Prawdopodobieństwo": (1 - p_want), "Wartość": V_alone},
]
EV2 = sum(l["Prawdopodobieństwo"] * l["Wartość"] for l in leaves_2)

leaves_3 = [
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Wykryto, nowa chce, lepsza",
     "Prawdopodobieństwo": p_discover * p_want_two_fronts * p_better, "Wartość": V_better},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Wykryto, nowa chce, gorsza",
     "Prawdopodobieństwo": p_discover * p_want_two_fronts * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Wykryto, nowa go olewa – sam",
     "Prawdopodobieństwo": p_discover * (1 - p_want_two_fronts), "Wartość": V_alone},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Nie wykryto, nowa chce, lepsza",
     "Prawdopodobieństwo": (1 - p_discover) * p_want_two_fronts * p_better, "Wartość": V_better},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Nie wykryto, nowa chce, gorsza",
     "Prawdopodobieństwo": (1 - p_discover) * p_want_two_fronts * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "3. Zaatakuje nową w tajemnicy", "Gałąź": "Nie wykryto, nowa olewa – zostaje z obecną",
     "Prawdopodobieństwo": (1 - p_discover) * (1 - p_want_two_fronts), "Wartość": V_stay},
]
EV3 = sum(l["Prawdopodobieństwo"] * l["Wartość"] for l in leaves_3)

evs = {
    "Pozostaje wierny": EV1,
    "Zrywam i atakuje nową": EV2,
    "Zaatakuje nową w tajemnicy": EV3,
}
best = max(evs, key=evs.get)

# ---------------------------------------------------------------------------
# WYNIKI - KARTY
# ---------------------------------------------------------------------------
st.markdown("### Wyniki – Expected Value")

c1, c2, c3 = st.columns(3)
for c, (name, val) in zip([c1, c2, c3], evs.items()):
    with c:
        cls = "ev-card best" if name == best else "ev-card"
        badge = '<div class="ev-badge">Najlepsza</div>' if name == best else ""
        st.markdown(
            f'<div class="{cls}">'
            f'<div class="ev-label">{name}</div>'
            f'<p class="ev-value">EV = {val:.1f}</p>'
            f'{badge}</div>',
            unsafe_allow_html=True,
        )

st.caption(
    f"Efektywna szansa, że nowa chce (gra na dwa fronty): "
    f"{p_want*100:.0f}% × {TWO_FRONTS_MULTIPLIER} = {p_want_two_fronts*100:.0f}%"
)

# ---------------------------------------------------------------------------
# WYKRES - poprawny, interaktywny, pokazuje wartości ujemne
# ---------------------------------------------------------------------------
labels = ["Zostań", "Zerwij", "Po Cichu"]
values = [EV1, EV2, EV3]
base_colors = ["#5B9BD5", "#70AD47", "#ED7D31"]
# podświetl najlepszą
best_idx = values.index(max(values))
colors = [
    c if i == best_idx else c + "AA"  # dodaj przezroczystość dla nie-najlepszych
    for i, c in enumerate(base_colors)
]

y_max = max(100, max(values) + 15)
y_min = min(-100, min(values) - 15)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=labels,
    y=values,
    marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.15)", width=1)),
    text=[f"{v:.1f}" for v in values],
    textposition="outside",
    textfont=dict(size=14, color="#222"),
    width=0.55,
    hovertemplate="<b>%{x}</b><br>EV = %{y:.2f}<extra></extra>",
))
# linia zero
fig.add_hline(y=0, line_width=1.5, line_color="#888")

fig.update_layout(
    title=dict(text="Expected Value (EV) dla każdej strategii", x=0.02, font=dict(size=16, color="#333")),
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)",
    height=450,
    margin=dict(t=70, l=20, r=20, b=40),
    yaxis=dict(
        range=[y_min, y_max],
        dtick=25,
        gridcolor="#EDEDED",
        zeroline=False,
        title="EV",
    ),
    xaxis=dict(showgrid=False),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# PEŁNE ROZBICIE
# ---------------------------------------------------------------------------
st.markdown("### Pełne rozbicie")

all_leaves = leaves_1 + leaves_2 + leaves_3
df = pd.DataFrame(all_leaves)
df["Wkład do EV"] = (df["Prawdopodobieństwo"] * df["Wartość"]).round(2)
df["Prawdopodobieństwo"] = (df["Prawdopodobieństwo"] * 100).round(1).astype(str) + "%"
df["Wartość"] = df["Wartość"].round(1)

strat_names = {
    "1. Pozostaje wierny": "1. Zostaje z obecną",
    "2. Zrywam i atakuje nową": "2. Zrywa i podrywa nową",
    "3. Zaatakuje nową w tajemnicy": "3. Zagaduje bez zrywania",
}
ev_lookup = {"1. Pozostaje wierny": EV1, "2. Zrywam i atakuje nową": EV2, "3. Zaatakuje nową w tajemnicy": EV3}

for strat, display_name in strat_names.items():
    with st.expander(f"{display_name} → EV = {ev_lookup[strat]:.2f}"):
        st.dataframe(
            df[df["Strategia"] == strat][["Gałąź", "Prawdopodobieństwo", "Wartość", "Wkład do EV"]],
            use_container_width=True,
            hide_index=True,
        )
