import base64
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Rozterki małżeńskie", layout="wide")

# ---------------------------------------------------------------------------
# DEKORACJE — wczytanie wygenerowanych "nitkowych" wirów SVG
# ---------------------------------------------------------------------------
with open("swirl_blue.svg", "r") as f:
    SWIRL_BLUE = base64.b64encode(f.read().encode()).decode()
with open("swirl_rose.svg", "r") as f:
    SWIRL_ROSE = base64.b64encode(f.read().encode()).decode()

# ---------------------------------------------------------------------------
# STYLE — czcionki, paleta, tło, komponenty
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600;700&display=swap');

    :root {{
        --bg:            #FAF6EF;
        --ink:           #2A2233;
        --ink-soft:      #6B6376;
        --card:          #FFFFFF;
        --border:        #ECE3D6;
        --plum:          #7A2E63;
        --plum-light:    #A9639A;
        --plum-pale:     #F2E4EE;
        --blue:          #3E7CB1;
        --green:         #3E8E63;
        --amber:         #C1662B;
        --shadow:        0 10px 30px -14px rgba(42, 34, 51, 0.25);
    }}

    /* ---- tło strony + wiry w rogach ---- */
    .stApp {{
        background: var(--bg);
        position: relative;
        overflow-x: hidden;
    }}
    .stApp::before, .stApp::after,
    .swirl-corner {{
        content: "";
        position: fixed;
        width: 620px;
        height: 620px;
        pointer-events: none;
        z-index: 0;
        background-repeat: no-repeat;
        background-size: contain;
    }}
    .swirl-tl {{
        top: -180px; left: -200px;
        background-image: url("data:image/svg+xml;base64,{SWIRL_BLUE}");
    }}
    .swirl-br {{
        bottom: -200px; right: -180px;
        background-image: url("data:image/svg+xml;base64,{SWIRL_ROSE}");
        transform: rotate(20deg);
    }}
    .swirl-tr {{
        top: -220px; right: -220px;
        width: 420px; height: 420px;
        background-image: url("data:image/svg+xml;base64,{SWIRL_ROSE}");
        opacity: 0.55;
    }}
    .swirl-bl {{
        bottom: -220px; left: -220px;
        width: 420px; height: 420px;
        background-image: url("data:image/svg+xml;base64,{SWIRL_BLUE}");
        opacity: 0.55;
        transform: rotate(-15deg);
    }}

    /* treść ponad dekoracją */
    .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 2.4rem;
        max-width: 1180px;
    }}

    /* ---- typografia ---- */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: var(--ink);
    }}
    h1 {{
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        font-size: 2.6rem !important;
        color: var(--ink) !important;
        letter-spacing: -0.01em;
        text-align: center;
    }}
    h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        color: var(--plum) !important;
    }}
    .stCaption, [data-testid="stCaptionContainer"] p {{
        text-align: center;
        color: var(--ink-soft) !important;
        font-style: italic;
    }}
    hr {{
        border-top: 1px solid var(--border) !important;
    }}

    /* ---- suwaki ---- */
    div[data-baseweb="slider"] {{
        padding-top: 6px;
    }}
    div[data-baseweb="slider"] > div > div > div {{
        background: linear-gradient(90deg, var(--plum-light), var(--plum)) !important;
    }}
    div[data-baseweb="slider"] div[role="slider"] {{
        background-color: var(--plum) !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(122, 46, 99, 0.45) !important;
        width: 20px !important;
        height: 20px !important;
    }}
    div[data-baseweb="slider"] div[data-testid="stTickBar"] {{
        display: none;
    }}
    .stSlider label p {{
        font-weight: 600 !important;
        color: var(--ink) !important;
    }}
    div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] {{
        color: var(--ink-soft) !important;
    }}

    /* wartość liczbowa nad suwakiem */
    div[data-testid="stThumbValue"] {{
        background-color: var(--plum) !important;
        color: #fff !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }}

    /* ---- karty wyników ---- */
    .ev-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 22px 18px 18px 18px;
        text-align: center;
        box-shadow: var(--shadow);
    }}
    .ev-card .name {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--ink-soft);
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }}
    .ev-card .value {{
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 2.4rem;
        color: var(--plum);
    }}
    .ev-card.best {{
        border: 1.5px solid var(--plum);
        background: var(--plum-pale);
    }}
    .ev-card .badge {{
        display: inline-block;
        margin-top: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        color: var(--plum);
        background: #fff;
        border: 1px solid var(--plum-light);
        border-radius: 999px;
        padding: 2px 10px;
    }}

    /* ---- expander / pełne rozbicie ---- */
    .streamlit-expanderHeader, details summary {{
        background: var(--card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        font-weight: 600 !important;
        color: var(--plum) !important;
    }}
    div[data-testid="stExpander"] {{
        border: none !important;
        margin-bottom: 10px;
    }}

    /* ---- tabela ---- */
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border);
    }}

    /* ---- wykres w karcie ---- */
    .chart-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px;
        box-shadow: var(--shadow);
    }}
    </style>

    <div class="swirl-corner swirl-tl"></div>
    <div class="swirl-corner swirl-br"></div>
    <div class="swirl-corner swirl-tr"></div>
    <div class="swirl-corner swirl-bl"></div>
    """,
    unsafe_allow_html=True,
)

st.title("Rozterki małżeńskie")
st.caption(
    "UWAGA gra na dwa fronty redukuje szanse o 20% na nowy nabytej tj. "
    "jeśli 50% redukcja=50\\*0,2=10%"
)

st.divider()

# ---------------------------------------------------------------------------
# WEJŚCIA UŻYTKOWNIKA
# ---------------------------------------------------------------------------
st.subheader("Prawdopodobieństwo")

col1, col2, col3 = st.columns(3)
with col1:
    p_better = st.slider("Nowa lepsza", 0, 100, 50, format="%d%%") / 100
with col2:
    p_want = st.slider("udany atak na serce nowej", 0, 100, 50, format="%d%%") / 100
with col3:
    p_discover = st.slider("obecna dowie się o twoich intrygach i zrywa", 0, 100, 30, format="%d%%") / 100

st.subheader("Wartości")

col4, col5, col6, col7 = st.columns(4)
with col4:
    V_stay = st.slider("obecny związek", -100, 100, 20)
with col5:
    V_alone = st.slider("samotność", -100, 100, -12)
with col6:
    V_better = st.slider("nowy związek gdy lepsza", -100, 100, 70)
with col7:
    V_worse = st.slider("Nowa gdy gorsza", -100, 100, -50)

st.divider()

# ---------------------------------------------------------------------------
# LOGIKA MODELU
# ---------------------------------------------------------------------------
# Redukcja szansy u nowej, gdy gra się na dwa fronty (opcja 3 - nie zrywa,
# ale zagaduje nową w tajemnicy): efektywna szansa = szansa * 0,2
# np. 50% -> 50 * 0,2 = 10%
TWO_FRONTS_MULTIPLIER = 0.2
p_want_two_fronts = p_want * TWO_FRONTS_MULTIPLIER

# --- Opcja 1: Zostań (pozostaje wierny) --------------------------------------
leaves_1 = [
    {"Strategia": "1. Pozostaje wierny", "Gałąź": "Zostaje z obecną",
     "Prawdopodobieństwo": 1.0, "Wartość": V_stay},
]
EV1 = V_stay

# --- Opcja 2: Zerwij (zrywam i atakuje nową) ---------------------------------
leaves_2 = [
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa chce, okazuje się lepsza",
     "Prawdopodobieństwo": p_want * p_better, "Wartość": V_better},
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa chce, okazuje się gorsza",
     "Prawdopodobieństwo": p_want * (1 - p_better), "Wartość": V_worse},
    {"Strategia": "2. Zrywam i atakuje nową", "Gałąź": "Nowa nie chce – zostaje sam",
     "Prawdopodobieństwo": (1 - p_want), "Wartość": V_alone},
]
EV2 = sum(l["Prawdopodobieństwo"] * l["Wartość"] for l in leaves_2)

# --- Opcja 3: Po Cichu (zaatakuje nową w tajemnicy, gra na dwa fronty) -------
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
# WYNIKI
# ---------------------------------------------------------------------------
st.subheader("Wyniki — Expected Value")

c1, c2, c3 = st.columns(3)
for c, (name, val) in zip([c1, c2, c3], evs.items()):
    with c:
        is_best = "best" if name == best else ""
        badge = '<div class="badge">Najlepsza opcja</div>' if name == best else ""
        st.markdown(
            f"""
            <div class="ev-card {is_best}">
                <div class="name">{name}</div>
                <div class="value">{val:.0f}</div>
                {badge}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    f"Efektywna szansa, że nowa chce (gra na dwa fronty, opcja 3): "
    f"{p_want*100:.0f}% × {TWO_FRONTS_MULTIPLIER} = {p_want_two_fronts*100:.0f}%"
)

st.write("")

# --- Wykres słupkowy w nowej kolorystyce -------------------------------------
labels = ["Zostań", "Zerwij", "Po Cichu"]
values = [EV1, EV2, EV3]
colors = ["#3E7CB1", "#3E8E63", "#C1662B"]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=labels,
    y=values,
    marker_color=colors,
    marker_line_width=0,
    text=[f"{v:.0f}" for v in values],
    textposition="outside",
    textfont=dict(family="Inter, sans-serif", size=15, color="#2A2233"),
    width=0.5,
))
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#2A2233"),
    height=420,
    margin=dict(t=60, l=10, r=10, b=10),
    yaxis=dict(range=[-100, 100], dtick=50, gridcolor="#ECE3D6",
               zerolinecolor="#B9AEC2", zerolinewidth=1.5),
    xaxis=dict(showgrid=False),
    showlegend=False,
)
fig.add_annotation(
    text="Expected Value (EV) ↑", xref="paper", yref="paper",
    x=0, y=1.12, showarrow=False, font=dict(size=14, color="#6B6376"), align="left"
)
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# PEŁNE ROZBICIE
# ---------------------------------------------------------------------------
st.subheader("Pełne rozbicie")

all_leaves = leaves_1 + leaves_2 + leaves_3
df = pd.DataFrame(all_leaves)
df["Wkład do EV"] = df["Prawdopodobieństwo"] * df["Wartość"]
df["Prawdopodobieństwo"] = (df["Prawdopodobieństwo"] * 100).round(1).astype(str) + "%"
df["Wartość"] = df["Wartość"].round(1)
df["Wkład do EV"] = df["Wkład do EV"].round(2)

strat_names = {
    "1. Pozostaje wierny": "1. Zostaje z obecną",
    "2. Zrywam i atakuje nową": "2. Zrywa i podrywa nową",
    "3. Zaatakuje nową w tajemnicy": "3. Zagaduje bez zrywania",
}
ev_lookup = {"1. Pozostaje wierny": EV1, "2. Zrywam i atakuje nową": EV2, "3. Zaatakuje nową w tajemnicy": EV3}

for strat, display_name in strat_names.items():
    with st.expander(f"{display_name} → EV = {ev_lookup[strat]:.1f}"):
        st.dataframe(
            df[df["Strategia"] == strat][["Gałąź", "Prawdopodobieństwo", "Wartość", "Wkład do EV"]],
            use_container_width=True,
            hide_index=True,
        )
