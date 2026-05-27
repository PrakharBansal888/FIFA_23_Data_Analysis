import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA 23 Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1a1d27;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        border: 1px solid #2a2d3a;
    }
    .metric-card h2 { color: #00d4ff; margin: 0; font-size: 2rem; }
    .metric-card p  { color: #aaa; margin: 4px 0 0 0; font-size: 0.85rem; }
    .section-title  { color: #ffffff; font-size: 1.3rem; font-weight: 700; margin-bottom: 8px; }
    .player-card {
        background: #1a1d27;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2a2d3a;
    }
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }
    .tag-green  { background: #1a3a2a; color: #00e676; border: 1px solid #00e676; }
    .tag-red    { background: #3a1a1a; color: #ff5252; border: 1px solid #ff5252; }
    .tag-yellow { background: #3a3a1a; color: #ffd740; border: 1px solid #ffd740; }
</style>
""", unsafe_allow_html=True)

# ── Data loading & caching ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/FIFA23/FIFA23_official_data.csv')
    except FileNotFoundError:
        st.error(
            "**Data file not found.** Expected `data/FIFA23/FIFA23_official_data.csv`. "
            "Please run `python setup_data.py` or place the CSV in the correct location."
        )
        st.stop()
    except pd.errors.EmptyDataError:
        st.error("**Data file is empty.** The CSV file contains no data.")
        st.stop()
    except Exception as e:
        st.error(f"**Failed to load data:** {e}")
        st.stop()

    try:
        def parse_currency(val):
            if pd.isna(val) or val == '':
                return np.nan
            val = str(val).replace('€', '').strip()
            if 'M' in val:
                return float(val.replace('M', '')) * 1_000_000
            elif 'K' in val:
                return float(val.replace('K', '')) * 1_000
            else:
                return float(val) if val else np.nan

        df['wage_numeric']  = df['Wage'].apply(parse_currency)
        df['value_numeric'] = df['Value'].apply(parse_currency)

        # Clean position (strip HTML tags)
        df['Position_clean'] = df['Position'].str.replace(r'<[^>]+>', '', regex=True).str.strip()

        # Position groups
        pos_map = {
            'GK': 'GK',
            'CB': 'DEF', 'LB': 'DEF', 'RB': 'DEF', 'LWB': 'DEF', 'RWB': 'DEF',
            'CDM': 'MID', 'CM': 'MID', 'CAM': 'MID', 'LM': 'MID', 'RM': 'MID',
            'LCM': 'MID', 'RCM': 'MID', 'LAM': 'MID', 'RAM': 'MID',
            'LW': 'ATT', 'RW': 'ATT', 'ST': 'ATT', 'CF': 'ATT',
            'RF': 'ATT', 'LF': 'ATT', 'LS': 'ATT', 'RS': 'ATT', 'SS': 'ATT',
            'SUB': 'SUB', 'RES': 'RES'
        }
        df['pos_group'] = df['Position_clean'].map(pos_map).fillna('Other')

        # Z-score for wage (over/underpaid)
        df_valid = df[(df['Overall'] >= 50) & df['wage_numeric'].notna()].copy()
        df_valid['wage_zscore'] = stats.zscore(np.log1p(df_valid['wage_numeric']))
        df_valid['pay_status'] = pd.cut(
            df_valid['wage_zscore'],
            bins=[-np.inf, -1.5, 1.5, np.inf],
            labels=['Underpaid', 'Fair', 'Overpaid']
        )

        # Growth room
        df_valid['growth_room'] = df_valid['Potential'] - df_valid['Overall']

        return df_valid

    except KeyError as e:
        st.error(
            f"**Missing expected column:** {e}. "
            "The CSV may have different column names than expected."
        )
        st.stop()
    except Exception as e:
        st.error(f"**Error processing data:** {e}")
        st.stop()

try:
    df = load_data()
except Exception as e:
    st.error(f"**Unexpected error during data load:** {e}")
    st.stop()

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/FIFA_23_logo.svg/320px-FIFA_23_logo.svg.png", width=180)
st.sidebar.markdown("## 🎛️ Filters")

# Age range
age_min, age_max = int(df['Age'].min()), int(df['Age'].max())
age_range = st.sidebar.slider("Age Range", age_min, age_max, (16, 35))

# Overall range
ovr_min, ovr_max = int(df['Overall'].min()), int(df['Overall'].max())
ovr_range = st.sidebar.slider("Overall Rating", ovr_min, ovr_max, (60, 99))

# Position group
pos_groups = ['All'] + sorted(df['pos_group'].dropna().unique().tolist())
sel_pos = st.sidebar.selectbox("Position Group", pos_groups)

# Nationality
nations = ['All'] + sorted(df['Nationality'].dropna().unique().tolist())
sel_nation = st.sidebar.selectbox("Nationality", nations)

# Club
clubs = ['All'] + sorted(df['Club'].dropna().unique().tolist())
sel_club = st.sidebar.selectbox("Club", clubs)

# Apply filters
mask = (
    df['Age'].between(*age_range) &
    df['Overall'].between(*ovr_range)
)
if sel_pos    != 'All': mask &= df['pos_group']   == sel_pos
if sel_nation != 'All': mask &= df['Nationality'] == sel_nation
if sel_club   != 'All': mask &= df['Club']        == sel_club

filtered = df[mask]

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# ⚽ FIFA 23 — Interactive Analytics Dashboard")
st.markdown(f"Showing **{len(filtered):,}** players based on current filters")
st.divider()

# ── KPI row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""<div class="metric-card">
        <h2>{len(filtered):,}</h2><p>Total Players</p></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card">
        <h2>{filtered['Overall'].mean():.1f}</h2><p>Avg Overall</p></div>""", unsafe_allow_html=True)
with k3:
    avg_wage = filtered['wage_numeric'].mean()
    st.markdown(f"""<div class="metric-card">
        <h2>€{avg_wage/1000:.1f}K</h2><p>Avg Weekly Wage</p></div>""", unsafe_allow_html=True)
with k4:
    avg_val = filtered['value_numeric'].mean() if filtered['value_numeric'].notna().any() else 0
    st.markdown(f"""<div class="metric-card">
        <h2>€{avg_val/1_000_000:.1f}M</h2><p>Avg Market Value</p></div>""", unsafe_allow_html=True)
with k5:
    avg_age = filtered['Age'].mean()
    st.markdown(f"""<div class="metric-card">
        <h2>{avg_age:.1f}</h2><p>Avg Age</p></div>""", unsafe_allow_html=True)

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Wages & Value",
    "🔍 Player Search",
    "🌍 Nations & Positions",
    "💎 Best Value XI"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Wages & Value
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-title">Wage vs Overall Rating</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Scatter: wage vs overall
        sample = filtered.sample(min(2000, len(filtered)), random_state=42) if len(filtered) > 2000 else filtered
        fig = px.scatter(
            sample,
            x='Overall', y='wage_numeric',
            color='pos_group',
            hover_data=['Name', 'Club', 'Nationality'],
            opacity=0.6,
            title='Wages vs Overall Rating',
            labels={'wage_numeric': 'Weekly Wage (€)', 'Overall': 'Overall Rating', 'pos_group': 'Position'},
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        # Median trend line
        trend = filtered.groupby('Overall')['wage_numeric'].median().reset_index()
        fig.add_trace(go.Scatter(
            x=trend['Overall'], y=trend['wage_numeric'],
            mode='lines', name='Median',
            line=dict(color='white', width=2, dash='dash')
        ))
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Wage vs Market Value
        plot_data = filtered[filtered['value_numeric'].notna()].copy()
        plot_data['wage_k']   = plot_data['wage_numeric'] / 1000
        plot_data['value_m']  = plot_data['value_numeric'] / 1_000_000
        sample2 = plot_data.sample(min(2000, len(plot_data)), random_state=1) if len(plot_data) > 2000 else plot_data

        fig2 = px.scatter(
            sample2,
            x='wage_k', y='value_m',
            color='Overall',
            color_continuous_scale='RdYlGn',
            hover_data=['Name', 'Club', 'pos_group'],
            opacity=0.6,
            title='Weekly Wage (€K) vs Market Value (€M)',
            labels={'wage_k': 'Weekly Wage (€K)', 'value_m': 'Market Value (€M)', 'Overall': 'Overall'},
            template='plotly_dark'
        )
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown('<p class="section-title">Pay Status Distribution</p>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        pay_counts = filtered['pay_status'].value_counts().reset_index()
        pay_counts.columns = ['Status', 'Count']
        color_map = {'Overpaid': '#ff5252', 'Fair': '#ffd740', 'Underpaid': '#00e676'}
        fig3 = px.pie(
            pay_counts, names='Status', values='Count',
            color='Status', color_discrete_map=color_map,
            title='Pay Status of Filtered Players',
            template='plotly_dark', hole=0.4
        )
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Top 10 earners in filtered set
        top_earners = filtered.nlargest(10, 'wage_numeric')[['Name', 'Club', 'Overall', 'wage_numeric', 'pos_group']]
        top_earners['Wage (€K/wk)'] = (top_earners['wage_numeric'] / 1000).round(1)
        st.markdown("**Top 10 Earners in Current Filter**")
        st.dataframe(
            top_earners[['Name', 'Club', 'Overall', 'pos_group', 'Wage (€K/wk)']].rename(
                columns={'pos_group': 'Position'}
            ).reset_index(drop=True),
            use_container_width=True, height=340
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Player Search
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">🔍 Search a Player</p>', unsafe_allow_html=True)

    search_query = st.text_input("Type a player name", placeholder="e.g. Messi, Ronaldo, Mbappe...")

    if search_query:
        results = df[df['Name'].str.contains(search_query, case=False, na=False)]

        if results.empty:
            st.warning(f"No players found matching '{search_query}'")
        else:
            if len(results) > 1:
                player_names = results['Name'].tolist()
                selected_name = st.selectbox("Multiple matches — select one:", player_names)
                player = results[results['Name'] == selected_name].iloc[0]
            else:
                player = results.iloc[0]

            # Player card
            col_a, col_b, col_c = st.columns([1, 2, 2])

            with col_a:
                st.markdown(f"""
                <div class="player-card" style="text-align:center">
                    <img src="{player.get('Photo', '')}" width="100" style="border-radius:50%;border:3px solid #00d4ff"/>
                    <h3 style="color:white;margin:10px 0 4px 0">{player['Name']}</h3>
                    <p style="color:#aaa;margin:0">{player['Club']}</p>
                    <img src="{player.get('Flag', '')}" width="30" style="margin-top:8px"/>
                    <p style="color:#aaa;margin:4px 0 0 0">{player['Nationality']}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown("**📋 Player Stats**")
                wage_k  = player['wage_numeric'] / 1000 if pd.notna(player['wage_numeric']) else 0
                value_m = player['value_numeric'] / 1_000_000 if pd.notna(player['value_numeric']) else 0

                stats_data = {
                    "Overall":       player['Overall'],
                    "Potential":     player['Potential'],
                    "Age":           player['Age'],
                    "Position":      player['Position_clean'],
                    "Weekly Wage":   f"€{wage_k:.1f}K",
                    "Market Value":  f"€{value_m:.1f}M",
                    "Nationality":   player['Nationality'],
                    "Contract Until": player.get('Contract Valid Until', 'N/A'),
                    "Height":        player.get('Height', 'N/A'),
                    "Weight":        player.get('Weight', 'N/A'),
                }
                for k, v in stats_data.items():
                    st.markdown(f"**{k}:** {v}")

            with col_c:
                st.markdown("**💰 Wage & Value Analysis**")

                pay_status = player.get('pay_status', 'N/A')
                tag_class  = {'Overpaid': 'tag-red', 'Underpaid': 'tag-green', 'Fair': 'tag-yellow'}.get(str(pay_status), 'tag-yellow')
                st.markdown(f'<span class="tag {tag_class}">{pay_status}</span>', unsafe_allow_html=True)

                zscore = player.get('wage_zscore', 0)
                st.markdown(f"**Wage Z-Score:** `{zscore:.2f}` *(0 = perfectly average for their rating)*")

                # How does this player's wage compare to others at same overall?
                same_ovr = df[df['Overall'] == player['Overall']]['wage_numeric']
                pct = (same_ovr < player['wage_numeric']).mean() * 100
                st.markdown(f"**Earns more than:** `{pct:.0f}%` of players with same Overall rating")

                growth = player['growth_room']
                st.markdown(f"**Growth Room:** `+{growth}` points *(Potential - Overall)*")

                # Mini radar: overall, potential, age context
                categories = ['Overall', 'Potential', 'Age-inverted']
                age_inv = max(0, 100 - (player['Age'] - 16) * 2.5)
                values  = [player['Overall'], player['Potential'], age_inv]

                fig_r = go.Figure(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor='rgba(0,212,255,0.15)',
                    line=dict(color='#00d4ff', width=2)
                ))
                fig_r.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color='gray'),
                        bgcolor='#1a1d27'
                    ),
                    paper_bgcolor='#1a1d27',
                    font_color='white',
                    height=260,
                    margin=dict(l=40, r=40, t=20, b=20)
                )
                st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("👆 Type a player name above to see their full profile and wage analysis.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Nations & Positions
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">🌍 Players by Nation (Top 20)</p>', unsafe_allow_html=True)
        top_nations = filtered['Nationality'].value_counts().head(20).reset_index()
        top_nations.columns = ['Country', 'Players']
        fig_n = px.bar(
            top_nations, x='Players', y='Country',
            orientation='h',
            color='Players', color_continuous_scale='Blues',
            template='plotly_dark',
            title='Top 20 Nationalities in Current Filter'
        )
        fig_n.update_layout(coloraxis_showscale=False, height=480,
                            yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_n, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">📍 Position Distribution</p>', unsafe_allow_html=True)
        pos_counts = filtered['pos_group'].value_counts().reset_index()
        pos_counts.columns = ['Position', 'Count']
        fig_p = px.pie(
            pos_counts, names='Position', values='Count',
            color_discrete_sequence=px.colors.qualitative.Bold,
            template='plotly_dark', hole=0.35,
            title='Player Distribution by Position Group'
        )
        fig_p.update_layout(height=480)
        st.plotly_chart(fig_p, use_container_width=True)

    st.divider()

    # World choropleth
    st.markdown('<p class="section-title">🗺️ World Map — Elite Players (Overall ≥ 75)</p>', unsafe_allow_html=True)
    elite = filtered[filtered['Overall'] >= 75]
    nation_map = elite['Nationality'].value_counts().reset_index()
    nation_map.columns = ['Country', 'Count']

    fig_map = px.choropleth(
        nation_map,
        locations='Country',
        locationmode='country names',
        color='Count',
        color_continuous_scale='YlOrRd',
        template='plotly_dark',
        title='Countries Producing Elite Players (Overall ≥ 75)',
        labels={'Count': 'Elite Players'}
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True,
                 projection_type='natural earth', bgcolor='#0e1117'),
        paper_bgcolor='#0e1117',
        height=460
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Avg overall by position
    st.markdown('<p class="section-title">📊 Average Overall by Position</p>', unsafe_allow_html=True)
    pos_ovr = filtered.groupby('Position_clean')['Overall'].agg(['mean', 'count']).reset_index()
    pos_ovr = pos_ovr[pos_ovr['count'] >= 10].sort_values('mean', ascending=False).head(20)
    pos_ovr.columns = ['Position', 'Avg Overall', 'Count']

    fig_po = px.bar(
        pos_ovr, x='Position', y='Avg Overall',
        color='Avg Overall', color_continuous_scale='Viridis',
        template='plotly_dark',
        title='Average Overall Rating by Position (min 10 players)'
    )
    fig_po.update_layout(coloraxis_showscale=False, height=380)
    st.plotly_chart(fig_po, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Best Value XI
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">💎 Auto-Pick Best Value XI</p>', unsafe_allow_html=True)
    st.markdown("Set a **weekly wage budget** and we'll auto-pick the best 11 undervalued players for a full squad.")

    budget = st.slider(
        "Total Weekly Wage Budget (€K)",
        min_value=50, max_value=2000, value=500, step=50
    )
    budget_euros = budget * 1000

    formation = st.selectbox("Formation", ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1"])

    formation_slots = {
        "4-3-3":  {'GK': 1, 'DEF': 4, 'MID': 3, 'ATT': 3},
        "4-4-2":  {'GK': 1, 'DEF': 4, 'MID': 4, 'ATT': 2},
        "3-5-2":  {'GK': 1, 'DEF': 3, 'MID': 5, 'ATT': 2},
        "4-2-3-1":{'GK': 1, 'DEF': 4, 'MID': 5, 'ATT': 1},
    }
    slots = formation_slots[formation]

    if st.button("🔍 Pick My XI", type="primary"):
        squad = []
        total_wage = 0
        remaining_budget = budget_euros

        eligible = df[
            df['wage_numeric'].notna() &
            df['pos_group'].isin(['GK', 'DEF', 'MID', 'ATT'])
        ].copy()

        # Value score: overall per € of wage
        eligible['value_score'] = eligible['Overall'] / (eligible['wage_numeric'] / 1000 + 1)

        used_ids = set()

        for pos_group, count in slots.items():
            pos_pool = eligible[
                (eligible['pos_group'] == pos_group) &
                (~eligible.index.isin(used_ids)) &
                (eligible['wage_numeric'] <= remaining_budget * (count / (11 - len(squad) + 0.001) + 0.3))
            ].nlargest(count * 5, 'value_score')  # top candidates

            # Greedy pick: best value score that fits budget
            picked = 0
            for _, row in pos_pool.iterrows():
                if picked >= count:
                    break
                if total_wage + row['wage_numeric'] <= budget_euros:
                    squad.append(row)
                    total_wage += row['wage_numeric']
                    used_ids.add(row.name)
                    picked += 1

        if len(squad) == 11:
            squad_df = pd.DataFrame(squad)

            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Players Found", "11 / 11 ✅")
            m2.metric("Total Weekly Wage", f"€{total_wage/1000:.1f}K")
            m3.metric("Budget Remaining", f"€{(budget_euros - total_wage)/1000:.1f}K")
            m4.metric("Avg Overall", f"{squad_df['Overall'].mean():.1f}")

            st.divider()

            # Squad table
            squad_display = squad_df[['Name', 'Age', 'pos_group', 'Overall', 'Potential', 'Club', 'Nationality', 'wage_numeric', 'value_score']].copy()
            squad_display['Wage (€K/wk)']  = (squad_display['wage_numeric'] / 1000).round(1)
            squad_display['Value Score']    = squad_display['value_score'].round(2)
            squad_display = squad_display.rename(columns={'pos_group': 'Position'})
            squad_display = squad_display.drop(columns=['wage_numeric', 'value_score'])

            st.markdown("**Your Best Value XI:**")
            st.dataframe(squad_display.reset_index(drop=True), use_container_width=True, height=420)

            # Wage breakdown by position
            wage_by_pos = squad_df.groupby('pos_group')['wage_numeric'].sum().reset_index()
            wage_by_pos.columns = ['Position', 'Total Wage']
            fig_xi = px.pie(
                wage_by_pos, names='Position', values='Total Wage',
                title='Wage Budget Split by Position',
                color_discrete_sequence=px.colors.qualitative.Bold,
                template='plotly_dark', hole=0.4
            )
            fig_xi.update_layout(height=350)
            st.plotly_chart(fig_xi, use_container_width=True)

        else:
            st.error(f"⚠️ Could only find {len(squad)} players within a €{budget}K/week budget. Try increasing the budget.")

    else:
        st.info("👆 Set your budget, choose a formation, and click **Pick My XI**.")
