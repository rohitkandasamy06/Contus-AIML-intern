"""
AutoParts Operations Analytics Dashboard
Maruti Suzuki Genuine Parts inspired design
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import data_access as da

st.set_page_config(
    page_title="AutoParts Ops | Chennai",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&family=Roboto+Condensed:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }

/* ── Base ── */
.stApp { background: #F0F2F5; color: #1A1A2E; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #003087 !important;
    border-right: 4px solid #C41E3A !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stDateInput > div > div > input {
    background: #00226B !important;
    border: 1px solid #0052CC !important;
    color: #FFFFFF !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #A8C4FF !important;
}
[data-testid="stSidebar"] .stSelectbox svg { fill: #FFFFFF !important; }

/* ── Top nav bar ── */
.topbar {
    background: linear-gradient(135deg, #003087 0%, #001F5E 100%);
    padding: 0;
    margin: -1rem -1rem 0 -1rem;
    border-bottom: 4px solid #C41E3A;
}
.topbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 32px;
}
.brand-left { display: flex; align-items: center; gap: 16px; }
.brand-logo {
    background: #C41E3A;
    color: white;
    font-size: 1.4rem;
    font-weight: 900;
    width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 6px;
    letter-spacing: -1px;
    font-family: 'Roboto Condensed', sans-serif;
}
.brand-name {
    color: #FFFFFF;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1.2;
}
.brand-sub {
    color: #A8C4FF;
    font-size: 0.68rem;
    font-weight: 400;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.badge-genuine {
    background: #C41E3A;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
}

/* ── Section title ── */
.section-title {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #003087;
    border-left: 4px solid #C41E3A;
    padding-left: 10px;
    margin: 28px 0 16px 0;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DDE3EE;
    border-radius: 6px;
    padding: 18px 20px;
    border-top: 4px solid #003087;
    box-shadow: 0 2px 8px rgba(0,48,135,0.07);
}
.kpi-card.alert { border-top-color: #C41E3A; }
.kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6B7898;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #003087;
    line-height: 1;
}
.kpi-value.red { color: #C41E3A; }
.kpi-value.green { color: #0A7C47; }
.kpi-sub {
    font-size: 0.7rem;
    color: #6B7898;
    margin-top: 5px;
}

/* ── Alert row ── */
.alert-row {
    background: #FFF5F5;
    border: 1px solid #FCCACA;
    border-left: 4px solid #C41E3A;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 0.8rem;
    margin: 4px 0;
    color: #1A1A2E;
}

/* ── Table style ── */
.quality-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.quality-table th {
    background: #003087; color: white;
    padding: 8px 12px; text-align: left;
    font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase;
}
.quality-table td { padding: 8px 12px; border-bottom: 1px solid #DDE3EE; }
.quality-table tr:nth-child(even) td { background: #F7F9FC; }

/* ── Divider ── */
.ms-divider {
    height: 2px;
    background: linear-gradient(90deg, #003087, #C41E3A, #F0F2F5);
    margin: 8px 0 24px 0;
    border: none;
}

/* ── Footer ── */
.ms-footer {
    background: #003087;
    color: #A8C4FF;
    text-align: center;
    font-size: 0.68rem;
    padding: 14px;
    margin: 32px -1rem -1rem -1rem;
    letter-spacing: 0.06em;
}
.ms-footer span { color: #C41E3A; font-weight: 700; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

CHART_BLUE   = "#003087"
CHART_RED    = "#C41E3A"
CHART_COLORS = ["#003087","#C41E3A","#0052CC","#E8810A","#0A7C47","#6B7898"]

def ms_theme(fig, title=""):
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Roboto", color="#1A1A2E", size=11),
        xaxis=dict(gridcolor="#EEF1F8", linecolor="#DDE3EE", tickcolor="#DDE3EE"),
        yaxis=dict(gridcolor="#EEF1F8", linecolor="#DDE3EE", tickcolor="#DDE3EE"),
        margin=dict(l=16, r=16, t=36, b=16),
        title=dict(text=title, font=dict(color="#003087", size=13, family="Roboto Condensed"), x=0),
        legend=dict(font=dict(color="#6B7898", size=10), bgcolor="rgba(0,0,0,0)")
    )
    return fig

# ── Topbar ────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-inner">
    <div class="brand-left">
      <div class="brand-logo">AP</div>
      <div>
        <div class="brand-name">AutoParts Operations Analytics</div>
        <div class="brand-sub">Chennai Auto Components Pvt. Ltd. · Internal Platform</div>
      </div>
    </div>
    <div class="badge-genuine">✦ Genuine Parts Division</div>
  </div>
</div>
<hr class="ms-divider"/>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 24px 0'>
        <div style='font-size:2rem;font-weight:900;color:white;font-family:Roboto Condensed,sans-serif;letter-spacing:-1px'>AP</div>
        <div style='font-size:0.7rem;color:#A8C4FF;letter-spacing:0.12em;text-transform:uppercase;margin-top:2px'>Operations Hub</div>
    </div>
    <hr style='border:1px solid #0052CC;margin-bottom:20px'/>
    """, unsafe_allow_html=True)

    min_date, max_date = da.get_date_range()
    start_date = st.date_input("Start Date", min_date)
    end_date   = st.date_input("End Date",   max_date)
    st.markdown("<div style='margin:8px 0'/>", unsafe_allow_html=True)
    category   = st.selectbox("Product Category", da.get_categories())
    carrier    = st.selectbox("Carrier", da.get_carriers())

    st.markdown("""
    <hr style='border:1px solid #0052CC;margin:20px 0 12px 0'/>
    <div style='font-size:0.68rem;color:#A8C4FF;line-height:1.8'>
        📅 Period: Jul 2025 – Jun 2026<br>
        🗄️ 10 Tables · ~16,000 Rows<br>
        📍 Chennai HQ + 3 Warehouses<br>
        🚚 5 Logistics Partners
    </div>
    """, unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

kpi  = da.get_kpis(start_date, end_date)
prod = da.get_production_kpis(start_date, end_date)
defect_pct = float(prod['defect_rate_pct'])
inv  = da.get_inventory_health()
n_alerts = len(inv[inv["below_reorder_level"] == True])

c1,c2,c3,c4,c5,c6 = st.columns(6)
kpi_data = [
    (c1, "Total Orders",    f"{int(kpi['total_orders']):,}",               "Fulfilled + Active",   "", False),
    (c2, "Revenue",         f"₹{float(kpi['total_revenue'])/100000:.1f}L", "Lakhs INR",            "", False),
    (c3, "Avg Order Value", f"₹{float(kpi['avg_order_value']):,.0f}",      "Per transaction",      "", False),
    (c4, "Units Produced",  f"{int(prod['total_produced']):,}",            "All production lines", "", False),
    (c5, "Defect Rate",     f"{defect_pct:.2f}%",
         "Target < 2%", "red" if defect_pct >= 2 else "green", defect_pct >= 3),
    (c6, "Reorder Alerts",  str(n_alerts),
         "Products low on stock", "red" if n_alerts > 0 else "green", n_alerts > 0),
]
for col, label, val, sub, cls, is_alert in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card {'alert' if is_alert else ''}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {cls}">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# ── Revenue + Category ────────────────────────────────────────
st.markdown('<div class="section-title">Revenue Analytics</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    rev = da.get_monthly_revenue(start_date, end_date, category)
    if not rev.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=rev["month"], y=rev["revenue"], mode="lines+markers",
            fill="tozeroy", fillcolor="rgba(0,48,135,0.08)",
            line=dict(color=CHART_BLUE, width=2.5),
            marker=dict(color=CHART_RED, size=6),
            name="Revenue"
        ))
        fig = ms_theme(fig, "Monthly Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    cat_rev = da.get_category_revenue(start_date, end_date)
    if not cat_rev.empty:
        fig2 = px.pie(cat_rev, names="category", values="revenue", hole=0.5,
                      color_discrete_sequence=CHART_COLORS)
        fig2.update_traces(textposition="outside", textfont_size=10)
        fig2 = ms_theme(fig2, "Revenue by Category")
        st.plotly_chart(fig2, use_container_width=True)

# ── Production ────────────────────────────────────────────────
st.markdown('<div class="section-title">Production Quality</div>', unsafe_allow_html=True)
col3, col4 = st.columns([3, 2])

with col3:
    mp = da.get_monthly_production(start_date, end_date)
    if not mp.empty:
        fig3 = go.Figure()
        fig3.add_bar(x=mp["month"], y=mp["total_produced"],
                     name="Produced", marker_color=CHART_BLUE, opacity=0.85)
        fig3.add_bar(x=mp["month"], y=mp["total_defective"],
                     name="Defective", marker_color=CHART_RED)
        fig3 = ms_theme(fig3, "Monthly Production vs Defects")
        fig3.update_layout(barmode="overlay",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    mach = da.get_machine_performance()
    if not mach.empty:
        mach_s = mach.sort_values("defect_rate_pct", ascending=True)
        bar_colors = [CHART_RED if r > 5 else "#E8810A" if r > 2 else "#0A7C47"
                      for r in mach_s["defect_rate_pct"]]
        fig4 = go.Figure(go.Bar(
            x=mach_s["defect_rate_pct"], y=mach_s["machine_code"],
            orientation="h", marker_color=bar_colors,
            text=[f"{r:.1f}%" for r in mach_s["defect_rate_pct"]],
            textposition="outside", textfont=dict(color="#1A1A2E", size=11)
        ))
        fig4.add_vline(x=2, line_dash="dash", line_color=CHART_RED,
                       annotation_text="2% limit", annotation_font_color=CHART_RED)
        fig4 = ms_theme(fig4, "Machine Defect Rate")
        st.plotly_chart(fig4, use_container_width=True)

# ── Logistics + Inventory ─────────────────────────────────────
st.markdown('<div class="section-title">Logistics & Inventory</div>', unsafe_allow_html=True)
col5, col6 = st.columns([3, 2])

with col5:
    dlv = da.get_delivery_performance(carrier)
    if not dlv.empty:
        dlv_s = dlv.sort_values("on_time_pct", ascending=True)
        bar_colors = [CHART_BLUE if p >= 80 else "#E8810A" if p >= 60 else CHART_RED
                      for p in dlv_s["on_time_pct"]]
        fig5 = go.Figure(go.Bar(
            x=dlv_s["on_time_pct"], y=dlv_s["carrier"],
            orientation="h", marker_color=bar_colors,
            text=[f"{p:.0f}%" for p in dlv_s["on_time_pct"]],
            textposition="outside", textfont=dict(color="#1A1A2E", size=11)
        ))
        fig5.add_vline(x=80, line_dash="dot", line_color=CHART_RED,
                       annotation_text="80% SLA", annotation_font_color=CHART_RED)
        fig5 = ms_theme(fig5, "On-Time Delivery by Carrier")
        fig5.update_layout(xaxis=dict(range=[0, 115]))
        st.plotly_chart(fig5, use_container_width=True)

with col6:
    alerts = inv[inv["below_reorder_level"] == True]
    st.markdown(f"""
    <div class="kpi-card {'alert' if len(alerts) > 0 else ''}">
        <div class="kpi-label">Inventory Reorder Alerts</div>
        <div class="kpi-value {'red' if len(alerts) > 0 else 'green'}">{len(alerts)} Items</div>
        <div class="kpi-sub">{'Immediate restocking required' if len(alerts) > 0 else 'All stock levels healthy'}</div>
    </div>
    <div style='margin-top:10px'>
    """, unsafe_allow_html=True)
    if not alerts.empty:
        for _, row in alerts.head(6).iterrows():
            st.markdown(f"""
            <div class="alert-row">
                <b>{row['product_name']}</b> &nbsp;·&nbsp; {row['city']}<br>
                <span style='color:#6B7898;font-size:0.72rem'>
                    Stock: <b style='color:#C41E3A'>{row['quantity_on_hand']}</b>
                    &nbsp;/&nbsp; Reorder at: {row['reorder_level']}
                </span>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Tickets + Top products ─────────────────────────────────────
st.markdown('<div class="section-title">Support & Product Performance</div>', unsafe_allow_html=True)
col7, col8 = st.columns(2)

with col7:
    tkt = da.get_ticket_summary(start_date, end_date)
    if not tkt.empty:
        color_map = {"Low":"#0A7C47","Medium":"#E8810A","High":"#C41E3A","Critical":"#6B0020"}
        fig6 = px.bar(tkt, x="issue_type", y="total", color="priority",
                      barmode="stack", color_discrete_map=color_map,
                      labels={"total": "Tickets", "issue_type": ""})
        fig6 = ms_theme(fig6, "Support Tickets by Issue Type & Priority")
        fig6.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig6, use_container_width=True)

with col8:
    top = da.get_top_products(start_date, end_date)
    if not top.empty:
        fig7 = px.bar(top, x="revenue", y="name", orientation="h",
                      color="category", color_discrete_sequence=CHART_COLORS,
                      labels={"revenue": "Revenue (₹)", "name": ""})
        fig7 = ms_theme(fig7, "Top 5 Products by Revenue")
        st.plotly_chart(fig7, use_container_width=True)

# ── Map ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Dealer & Customer Network</div>', unsafe_allow_html=True)
geo = da.get_customer_geo()
if not geo.empty:
    fig8 = px.scatter_mapbox(
        geo, lat="latitude", lon="longitude",
        size="lifetime_value", color="customer_type",
        hover_name="customer_name",
        hover_data={"city":True,"total_orders":True,"lifetime_value":True,
                    "latitude":False,"longitude":False},
        mapbox_style="open-street-map",
        zoom=4.2, center={"lat":15.5,"lon":80.0},
        color_discrete_sequence=[CHART_BLUE, CHART_RED, "#0A7C47"],
        size_max=35, opacity=0.85
    )
    fig8.update_layout(
        paper_bgcolor="#FFFFFF", margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(font=dict(color="#1A1A2E"), bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#DDE3EE", borderwidth=1)
    )
    st.plotly_chart(fig8, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown("""
<div class="ms-footer">
    <span>AutoParts</span> Operations Analytics Platform &nbsp;·&nbsp;
    Chennai Auto Components Pvt. Ltd. &nbsp;·&nbsp;
    FY 2025–26 &nbsp;·&nbsp; Synthetic Operational Data
</div>
""", unsafe_allow_html=True)