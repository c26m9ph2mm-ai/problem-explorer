import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Problem Explorer",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "37 sustainability & social innovation case studies."},
)

DATA_PATH = Path(__file__).parent / "data.json"
PROBLEMS = json.loads(DATA_PATH.read_text(encoding="utf-8"))

CATEGORIES = [
    "All",
    "Design & Durability",
    "Environment & Resources",
    "Market & Economy",
    "Society & Ethics",
    "Operations & Behavior",
]
CAT_COLORS = {
    "Design & Durability": "#f59e0b",
    "Environment & Resources": "#4cc9a1",
    "Market & Economy": "#a78bfa",
    "Society & Ethics": "#f472b6",
    "Operations & Behavior": "#60a5fa",
}

st.markdown(
    """
<style>
:root { --fg:#e8ecf1; --muted:#9aa4b2; --dim:#6b7280; --bg-card:#1c232f; --border:#2a3240; }
.stApp { background:#0f1419; }
.block-container { padding-top: 2rem; max-width: 1400px; }
h1, h2, h3, h4, h5, h6, p, li, span, div { color: var(--fg); }
[data-testid="stMarkdownContainer"] p { color: var(--fg); }

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-top: 3px solid var(--accent, #4cc9a1);
  border-radius: 12px;
  padding: 16px 18px 12px;
  margin-bottom: 8px;
  min-height: 155px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-num { font-size: 11px; color: var(--dim); font-weight: 600; letter-spacing: 0.1em; }
.card-title { font-size: 17px; font-weight: 600; letter-spacing: -0.01em; color: var(--fg); }
.card-example { font-size: 13px; color: var(--muted); line-height: 1.45; flex: 1; }
.card-category {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
}
.stButton > button {
  background: #252d3c !important;
  border: 1px solid var(--border) !important;
  color: var(--fg) !important;
  border-radius: 8px !important;
  width: 100%;
  font-size: 13px !important;
}
.stButton > button:hover {
  background: #2f394b !important;
  border-color: var(--muted) !important;
}
.stButton.primary-btn > button {
  background: var(--fg) !important;
  color: #0f1419 !important;
}

.detail-header {
  margin-bottom: 10px;
}
.detail-num { font-size: 12px; color: var(--dim); font-weight: 600; letter-spacing: 0.1em; }
.detail-title { font-size: 32px; font-weight: 700; letter-spacing: -0.02em; margin: 4px 0 10px; }
.detail-cat {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #0f1419;
}
.detail-example-label { font-size: 12px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 18px; font-weight: 600; }
.detail-example-val { font-size: 18px; color: #7aa8ff; font-weight: 500; margin-bottom: 6px; }
.detail-body h2 { font-size: 15px; color: #4cc9a1; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 22px; margin-bottom: 8px; }
.detail-body ul { padding-left: 20px; }
.detail-body li { margin-bottom: 4px; }

[data-testid="stSidebar"] { background: #161c26; }
[data-testid="stSidebar"] .stMarkdown { color: var(--fg); }
</style>
""",
    unsafe_allow_html=True,
)


def markdown_body(text: str) -> str:
    """Our stored bodies use '## Heading' and '• Bullet' — convert to real markdown."""
    lines = []
    in_list = False
    for raw in text.split("\n"):
        line = raw.rstrip()
        if line.startswith("• "):
            lines.append("- " + line[2:])
            in_list = True
        elif line.startswith("## "):
            if in_list:
                lines.append("")
                in_list = False
            lines.append(line)
        else:
            if in_list and not line:
                in_list = False
            lines.append(line)
    return "\n".join(lines)


def get_filtered(search: str, category: str):
    q = search.lower().strip()
    out = []
    for p in PROBLEMS:
        if category != "All" and p["category"] != category:
            continue
        if q:
            hay = (p["title"] + " " + p["example"] + " " + p["body"] + " " + p["category"]).lower()
            if q not in hay:
                continue
        out.append(p)
    return out


# ---------------- state + query params ----------------
qp = st.query_params
if "current" not in st.session_state:
    st.session_state.current = qp.get("p")

if "search" not in st.session_state:
    st.session_state.search = ""
if "category" not in st.session_state:
    st.session_state.category = "All"


def open_problem(num: str):
    st.session_state.current = num
    st.query_params["p"] = num


def close_problem():
    st.session_state.current = None
    if "p" in st.query_params:
        del st.query_params["p"]


# ---------------- header ----------------
top_l, top_r = st.columns([3, 2])
with top_l:
    st.markdown(
        "<h1 style='margin-bottom:0;font-size:28px'>Problem <span style='color:#4cc9a1'>Explorer</span></h1>"
        "<p style='color:#9aa4b2;margin-top:4px;margin-bottom:18px'>37 case studies in sustainability & social innovation</p>",
        unsafe_allow_html=True,
    )

# ---------------- filter controls ----------------
f1, f2 = st.columns([3, 2])
with f1:
    search = st.text_input(
        "Search",
        key="search",
        placeholder="Search by title, example, or keyword…",
        label_visibility="collapsed",
    )
with f2:
    category = st.selectbox(
        "Category",
        CATEGORIES,
        key="category",
        label_visibility="collapsed",
    )

filtered = get_filtered(search, category)

# ---------------- main ----------------
if st.session_state.current is None:
    # --- GRID VIEW ---
    st.caption(
        f"Showing **{len(filtered)}** of **{len(PROBLEMS)}** problems"
        + (f" · category: {category}" if category != "All" else "")
    )

    if not filtered:
        st.info("No problems match your search.")
    else:
        cols_per_row = 3
        for row_start in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row, gap="small")
            for ci, p in enumerate(filtered[row_start : row_start + cols_per_row]):
                with cols[ci]:
                    color = CAT_COLORS[p["category"]]
                    st.markdown(
                        f"""
<div class="card" style="--accent:{color}">
  <div class="card-num">№ {p['num']}</div>
  <div class="card-title">{p['title']}</div>
  <div class="card-example">{p['example']}</div>
  <div class="card-category" style="color:{color}">{p['category']}</div>
</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Read  →", key=f"open_{p['num']}", use_container_width=True):
                        open_problem(p["num"])
                        st.rerun()

else:
    # --- DETAIL VIEW ---
    num = st.session_state.current
    p = next((x for x in PROBLEMS if x["num"] == num), None)
    if p is None:
        close_problem()
        st.rerun()

    # Figure out prev/next within current filter context
    idx_in_filter = next((i for i, x in enumerate(filtered) if x["num"] == num), -1)
    if idx_in_filter == -1:
        # current problem no longer matches filter; nav the full list instead
        list_ctx = PROBLEMS
        idx_in_list = next((i for i, x in enumerate(list_ctx) if x["num"] == num), 0)
    else:
        list_ctx = filtered
        idx_in_list = idx_in_filter

    prev_p = list_ctx[idx_in_list - 1] if idx_in_list > 0 else None
    next_p = list_ctx[idx_in_list + 1] if idx_in_list < len(list_ctx) - 1 else None

    nav_back, nav_prev, nav_count, nav_next = st.columns([1.2, 2, 1, 2])
    with nav_back:
        if st.button("← Back to grid", use_container_width=True):
            close_problem()
            st.rerun()
    with nav_prev:
        if prev_p:
            if st.button(f"◂  № {prev_p['num']} {prev_p['title']}", key="prev", use_container_width=True):
                open_problem(prev_p["num"])
                st.rerun()
        else:
            st.button("◂", disabled=True, use_container_width=True, key="prev_disabled")
    with nav_count:
        st.markdown(
            f"<div style='text-align:center;color:#9aa4b2;font-size:13px;padding-top:8px'>{idx_in_list + 1} / {len(list_ctx)}</div>",
            unsafe_allow_html=True,
        )
    with nav_next:
        if next_p:
            if st.button(f"№ {next_p['num']} {next_p['title']}  ▸", key="next", use_container_width=True):
                open_problem(next_p["num"])
                st.rerun()
        else:
            st.button("▸", disabled=True, use_container_width=True, key="next_disabled")

    st.markdown("<hr style='margin:16px 0 8px;border-color:#2a3240'>", unsafe_allow_html=True)

    color = CAT_COLORS[p["category"]]
    st.markdown(
        f"""
<div class="detail-header">
  <div class="detail-num">№ {p['num']}</div>
  <div class="detail-title">{p['title']}</div>
  <span class="detail-cat" style="background:{color}">{p['category']}</span>
</div>
<div class="detail-example-label">Example</div>
<div class="detail-example-val">{p['example']}</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="detail-body">', unsafe_allow_html=True)
    st.markdown(markdown_body(p["body"]))
    st.markdown("</div>", unsafe_allow_html=True)
