import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import json
import matplotlib
import matplotlib.cm as cm
matplotlib.use('Agg') # to not open new window when using matplotlib
import matplotlib.colors as mcolors
import colorsys # Required for shading
from PIL import Image
import os
from plotly.colors import sample_colorscale

# -------------------------
# Page setup
# -------------------------

# -------------------------
# Configuration
# -------------------------

PATH_GEOJSON = "datasets/israel_map.geojson"

PAGE1_PATH = "datasets/page1_final.csv"

PAGE2_PATH = "datasets/page2_final.csv"

PAGE3_PATH = "datasets/page3_final.csv"

PATH_SHIP = "pictures/exodus.png"
PATH_PLANE_ETHIOPIA = "pictures/ethiopia.png"
PATH_PLANE_MODERN = "pictures/current.png"

# ==============================================================================
# PAGE 1: IMMIGRATION TRENDS
# ==============================================================================

# 1. Page Config MUST be the very first command (Global)
st.set_page_config(
    page_title="ניתוח עלייה: 2015-2024",
    page_icon="🇮🇱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* --- GENERAL SETTINGS --- */
    /* Keep the global layout LTR so the sidebar stays on the LEFT */
    .stApp {
        direction: ltr;
    }

    /* --- SIDEBAR STYLING --- */
    /* Force the sidebar content to be RTL (for Hebrew text) and aligned right */
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    /* HIDE the default Streamlit Navigation and Search Bar */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* FIX RADIO BUTTONS */
    /* Align the radio button container to the right */
    .stRadio [role="radiogroup"] {
        direction: rtl;
        text-align: right;
        justify-content: right;
    }
    /* Ensure the text labels in the radio buttons align correctly */
    .stRadio div[data-testid="stMarkdownContainer"] p {
        text-align: right;
    }

    /* --- MAIN CONTENT STYLING --- */
    /* Force the main page content to be RTL */
    .main .block-container {
        direction: rtl;
        text-align: right;
    }

    /* Headers and Text Alignment for Main Area */
    h1, h2, h3, h4, h5, h6, p, div {
        text-align: right;
    }
    
    /* --- METRIC BOX STYLING --- */
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 15px;
        border-right: 5px solid #0038b8;
        color: rgb(49, 51, 63);
        margin-bottom: 1rem;
        direction: rtl; /* Ensure content inside box is RTL */
    }
    .metric-label {
        font-size: 14px;
        margin-bottom: 5px;
        color: #555;
        text-align: right;
    }
    .metric-value-large {
        font-size: 2rem;
        font-weight: 600;
        color: #000;
        text-align: right;
    }
    .metric-value-list {
        font-size: 1.1rem;
        font-weight: 500;
        line-height: 1.6;
        color: #000;
        text-align: right;
    }

    /* Custom Page Headers */
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 3.5rem;
        color: #0038b8;
        text-align: center; /* Titles look better centered usually, change to right if preferred */
        font-weight: 800;
        text-shadow: 1px 1px 2px #abb7c4;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #555;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 300;
    }
    .section-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0038b8;
        border-bottom: 3px solid #0038b8;
        padding-bottom: 15px;
        margin-top: 50px;
        margin-bottom: 30px;
        text-align: right;
    }
    /* --- PROCESS CARD STYLING (For "What We Did") --- */
    .process-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-right: 4px solid #0038b8; /* Israel Blue Accent */
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); /* Subtle shadow */
        transition: transform 0.2s; /* Smooth animation on hover */
    }
    .process-card:hover {
        transform: translateY(-2px); /* Moves up slightly when hovered */
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .process-title {
        color: #0038b8;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 8px;
        display: block;
    }
    .process-text {
        font-size: 0.95rem;
        color: #555;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)


# 3. Sidebar Navigation (Custom Radio)
# We use st.sidebar.title to give it a header above the radio buttons
st.sidebar.title("תפריט ראשי")

page = st.sidebar.radio(
    "עבור אל", 
    ["דף הבית", "מגמות עלייה ממדינות מוצא", "מגמות קליטה לפי יישובים", "תחומי תעסוקה של עולים לפי מדינת מוצא"],
    label_visibility="collapsed",
    key="main_navigation_radio" # <--- This unique key prevents the error
)

if page == "דף הבית":
    
    # Function to safely load images
    def load_image(path):
        if os.path.exists(path):
            return Image.open(path)
        return None


    img_ship = load_image(PATH_SHIP)
    img_plane_ethiopia = load_image(PATH_PLANE_ETHIOPIA)
    img_plane_modern = load_image(PATH_PLANE_MODERN)

    # --- Header ---
    st.markdown('<div class="main-header">המסע הביתה</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">ניתוח נתונים ומגמות עלייה לישראל (2015 - 2024)</div>', unsafe_allow_html=True)
    st.divider()

    # --- Historical Section ---
    st.markdown('<div class="section-title">מורשת היסטורית</div>', unsafe_allow_html=True)

    col_hist_right, col_hist_left = st.columns([1, 1])

    with col_hist_left:
        if img_ship:
            st.image(img_ship, caption="ההתחלה: הגעה דרך הים (אוניית מעפילים היסטורית)", use_container_width=True)
        st.markdown("""
        מאז הקמת המדינה, העלייה היא ליבה הפועם של ישראל. 
        מאוניות המעפילים החשאיות של שנות ה-40, דרך גלי העלייה הגדולים מאירופה וארצות ערב.
        זהו סיפור על שיבה למולדת כנגד כל הסיכויים.
        """)

    with  col_hist_right:
        if img_plane_ethiopia:
            st.image(img_plane_ethiopia, caption="מבצע שלמה: הגעה ברכבת אווירית", use_container_width=True)
        st.markdown("""
        בשנות ה-80 וה-90, התבצעו מבצעים אוויריים נועזים להעלאת יהודי אתיופיה וברית המועצות לשעבר.
        תמונות אלו הן עדות למחויבות המתמשכת של מדינת ישראל לקיבוץ גלויות.
        """)

    # --- Modern Era Section ---
    st.markdown('<div class="section-title">הפרק הנוכחי: העידן המודרני (2015-2024)</div>', unsafe_allow_html=True)

    col_mod_right, col_mod_left = st.columns([2, 3])

    with col_mod_right:
        if img_plane_modern:
            st.image(img_plane_modern, caption="עלייה מודרנית: עולים חדשים מרוסיה נוחתים בישראל", use_container_width=True)

    with col_mod_left:
        st.markdown("""
        <div class="text-content" style="margin-top: 20px; direction: rtl;">
        הפרויקט שלנו מתמקד בעשור האחרון. <b>אמנם הנסיבות והאתגרים השתנו, אך הסיפור האנושי נשאר דומה.</b>
        <br><br>
        בשנים <b>2015-2024</b>, ישראל חוותה גלי עלייה משמעותיים המושפעים מאירועים גיאופוליטיים דרמטיים:
        המלחמה באוקראינה, התגברות האנטישמיות בעולם (במיוחד לאחר ה-7/10), ושינויים כלכליים גלובליים.
        <br><br>
        התמונה מימין מדגימה את העלייה העכשווית, הנמשכת בעוצמה גם בימים אלו, ומהווה עדות חיה לכך שסיפור עליית יהודי העולם ארצה רחוק מלהסתיים.
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- What We Did & Metrics ---
    st.markdown('<div class="section-title">תהליך המחקר והפיתוח</div>', unsafe_allow_html=True)

    c_cards_right, c_stats_left = st.columns([2, 1])

    with c_cards_right:
        st.markdown("""
        <div class="text-content" style="margin-bottom: 25px;">
        במסגרת הפרויקט, יצרנו מערכת אנליטית הבוחנת את מגמות העלייה לעומק.
        במקום להסתפק בסיכומים שנתיים, פירקנו את הנתונים לפי שלושה צירי מחקר עיקריים
        </div>
        """, unsafe_allow_html=True)

        grid_r1_c1, grid_r1_c2 = st.columns(2)
        grid_r2_c1, grid_r2_c2 = st.columns(2)

        # Card 1: The Technical Base
        with grid_r1_c1:
            st.markdown("""
            <div class="process-card">
                <span class="process-title">מגמות גלובליות</span>
                <span class="process-text">
                ניתוח עומק של מדינות המוצא מהן מגיעים העולים, זיהוי גלי הגירה ושינויים דמוגרפיים על ציר הזמן
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Card 2: Matches "מגמות עלייה ממדינות מוצא"
        with grid_r1_c2:
            st.markdown("""
            <div class="process-card">
                <span class="process-title">הנדסת נתונים</span>
                <span class="process-text">
                איסוף ואיחוד של רשומות עלייה גולמיות ממסדי נתונים ממשלתיים, ניקוי המידע ובניית דאטהסטים אחידים
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Card 3: Matches "מגמות קליטה לפי יישובים"
        with grid_r2_c1:
            st.markdown("""
            <div class="process-card">
                <span class="process-title">ניתוח קליטה ביישובים</span>
                <span class="process-text">
                מיפוי הערים הקולטות המובילות בישראל והבנת העדפות המגורים של עולים
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Card 4: Matches "תחומי תעסוקה..."
        with grid_r2_c2:
            st.markdown("""
            <div class="process-card">
                <span class="process-title">הון אנושי ותעסוקה</span>
                <span class="process-text">
                פילוח מקצועי של העולים לפי מדינות מוצא – איתור מגמות בתחומי ההייטק, הרפואה, ההנדסה והמקצועות החופשיים
                </span>
            </div>
            """, unsafe_allow_html=True)


    # 7. Metrics Section (Existing code, kept consistent)
    with c_stats_left:
        st.info(" **הצצה לנתונים**")

        # Mock Data Variables (Replace with your logic)
        total_olim_heb = 360000     
        top_country_heb = "רוסיה (159,748)"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">סה"כ עולים שנותחו (2015-2024)</div>
            <div class="metric-value-large">{total_olim_heb:,}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">מדינת המוצא המובילה</div>
            <div class="metric-value-large" style="font-size: 1.5rem;">{top_country_heb}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">3 הערים עם הכי הרבה עולים</div>
            <div class="metric-value-list">
                1. תל אביב (44,406)<br>
                2. נתניה (38,607)<br>
                3. חיפה (36,264)
            </div>
        </div>
        """, unsafe_allow_html=True)



elif page == "מגמות עלייה ממדינות מוצא":

    col_header_1, col_header_2 = st.columns([4, 1])
    with col_header_1:
        st.markdown("### 🌍✈️✡️")
    with col_header_2:
        st.title("עלייה לאורך השנים")
        st.caption("")

    @st.cache_data(show_spinner=False)
    def load_and_process_data(PAGE1_PATH):
        try:
            # We explicitly tell pandas to parse 'date' as dates
            df = pd.read_csv(PAGE1_PATH, parse_dates=["date"])
            hebrew_to_english = {}
            if "Country" in df.columns:
                temp_map = df[["erez_moza", "Country"]].dropna().drop_duplicates(subset=["erez_moza"])
                hebrew_to_english = temp_map.set_index("erez_moza")["Country"].to_dict()
            return df, hebrew_to_english, None
        except Exception as e:
            return None, None, None, f"Error loading Aggregated Immigration data: {e}"


    df_merged, hebrew_to_english, error = load_and_process_data(PAGE1_PATH)

    if error:
        st.error(error)
        st.stop()

    st.markdown("### פילטרים")
    c1, c2, c3 = st.columns([2, 2, 3])

    min_date = df_merged["date"].min()
    max_date = df_merged["date"].max()

    with c1:
        year_range = st.slider(
            "תחום שנים",
            int(min_date.year),
            int(max_date.year),
            (int(min_date.year), int(max_date.year))
        )

    with c2:
        speed_ms = st.slider("מהירות אנימציה (מילישניות)", 50, 500, 100, step=10)

    with c3:
        all_continents = sorted(df_merged["continent"].unique())
        selected_continents = st.multiselect("יבשות", all_continents, default=all_continents)

    timeline = pd.date_range(
        start=f"{year_range[0]}-01-01",
        end=f"{year_range[1]}-12-01",
        freq="MS"
    )

    base_filtered = df_merged[
        (df_merged["date"].isin(timeline)) &
        (df_merged["continent"].isin(selected_continents))
    ].copy()

    if base_filtered.empty:
        st.warning("לא נמצאו נתוני עלייה.")
        st.stop()

    default_colors = px.colors.qualitative.Plotly
    color_map = {continent: default_colors[i % len(default_colors)]
                 for i, continent in enumerate(all_continents)}
    if "צפון אמריקה" in color_map: color_map["צפון אמריקה"] = "#FFEA00"
    elif "North America" in color_map: color_map["North America"] = "#FFEA00"
    if "אוקיאניה" in color_map: color_map["אוקיאניה"] = "#D70040"
    if "אירופה" in color_map: color_map["אירופה"] = "#4169E1"

    col_chart, col_right = st.columns([5, 1.5])

    with col_right:
        map_placeholder = st.empty()
        st.markdown("#### בחר מדינות")

        country_stats = base_filtered.groupby("erez_moza")["monthly_count"].sum().sort_values(ascending=False)
        all_countries_sorted = sorted(base_filtered["erez_moza"].unique())
        default_top_25 = set(country_stats.index.tolist()[:25])

        for country in all_countries_sorted:
            key = f"chk_{country}"
            if key not in st.session_state:
                st.session_state[key] = country in default_top_25

        search_query = st.text_input("חפש מדינה", "", placeholder="הקלד לסינון...")
        visible_countries = [c for c in all_countries_sorted if search_query.lower() in c.lower()]

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("בחר הכל"):
            for country in visible_countries: st.session_state[f"chk_{country}"] = True
            st.rerun()
        if btn_col2.button("הסר הכל"):
            for country in visible_countries: st.session_state[f"chk_{country}"] = False
            st.rerun()

        selected_countries = []
        with st.container(height=350):
            for country in visible_countries:
                st.checkbox(country, key=f"chk_{country}")

        for country in all_countries_sorted:
            if st.session_state.get(f"chk_{country}", False):
                selected_countries.append(country)

        if not selected_countries:
            st.warning("Please select at least one country.")
            st.stop()

        map_data = (
            base_filtered.groupby(["erez_moza", "continent"], as_index=False)["monthly_count"]
            .sum()
            .rename(columns={"monthly_count": "total_immigrants"})
        )
        map_data["english_name"] = map_data["erez_moza"].map(hebrew_to_english)
        map_data["fmt_total"] = map_data["total_immigrants"].apply(lambda x: "{:,.0f}".format(x))
        map_selected = map_data[map_data["erez_moza"].isin(selected_countries)]

        map_hovertemplate = (
            "<b>%{customdata[2]}</b><br>" +
            "<span style='font-size: 10px; color: #666;'>%{customdata[0]}</span><br>" +
            "<extra></extra>"
        )

        if not map_data.empty:
            fig_map = go.Figure()
            fig_map.update_geos(
                showland=True, landcolor="#E0E0E0", showcountries=True,
                countrycolor="white", projection_type="natural earth",
                showframe=False, showcoastlines=False
            )
            base_choropleth = px.choropleth( #TODO
                map_data, locations="english_name", locationmode="country names",
                color="continent", color_discrete_map=color_map,
                category_orders={"continent": all_continents},
                hover_data=["continent", "fmt_total", "erez_moza"]
            )
            for trace in base_choropleth.data:
                trace.marker.opacity = 0.2
                trace.showlegend = False
                trace.hovertemplate = map_hovertemplate
                fig_map.add_trace(trace)

            if not map_selected.empty:
                highlight_choropleth = px.choropleth(
                    map_selected, locations="english_name", locationmode="country names",
                    color="continent", color_discrete_map=color_map,
                    category_orders={"continent": all_continents},
                    hover_data=["continent", "fmt_total", "erez_moza"]
                )
                for trace in highlight_choropleth.data:
                    trace.marker.opacity = 1.0
                    trace.showlegend = False
                    trace.hovertemplate = map_hovertemplate
                    fig_map.add_trace(trace)

            fig_map.update_layout(
                height=200, margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False, geo=dict(projection_scale=1.2)
            )
            map_placeholder.plotly_chart(fig_map, use_container_width=True)

    base_final = base_filtered[base_filtered["erez_moza"].isin(selected_countries)]
    grid = pd.MultiIndex.from_product(
        [timeline, selected_countries], names=["date", "erez_moza"]
    ).to_frame(index=False)

    grid = grid.merge(base_final, on=["date", "erez_moza"], how="left")
    
    # Fill missing immigration counts with 0 (months with no immigrants)
    grid["monthly_count"] = grid["monthly_count"].fillna(0)
    
    # Map continent to ensure the grid has it (using the map created from base_filtered)
    country_continent_map = base_filtered.groupby("erez_moza")["continent"].first()
    grid["continent"] = grid["erez_moza"].map(country_continent_map)

    grid = grid.dropna(subset=["gdp"])

    if grid.empty:
        st.error("No overlapping data found.")
        st.stop()

    grid = grid.sort_values(["erez_moza", "date"])
    grid["cumulative"] = grid.groupby("erez_moza")["monthly_count"].cumsum()
    grid["log_gdp"] = np.log1p(grid["gdp"])
    grid["sqrt_cumulative"] = np.sqrt(grid["cumulative"])
    grid["bubble_size"] = grid["monthly_count"].clip(lower=1) ** 0.6
    grid["month_str"] = grid["date"].dt.strftime("%Y-%m")

    grid["fmt_gdp"] = grid["gdp"].apply(lambda x: "${:,.0f}".format(x))
    grid["fmt_cum"] = grid["cumulative"].apply(lambda x: "{:,.0f}".format(x))
    grid["fmt_monthly"] = grid["monthly_count"].apply(lambda x: "{:,.0f}".format(x))

    x_min, x_max = grid["log_gdp"].min(), grid["log_gdp"].max()
    y_max = grid["sqrt_cumulative"].max()
    x_range = [x_min * 0.98, x_max * 1.02]
    y_range = [0, y_max * 1.05]

    with col_chart:
        st.subheader("""גרף אינטראקטיבי של עלייה מול תל"ג""")
        
        # 1. Create the base chart
        # We preserve your exact configuration here
        fig = px.scatter( #TODO
            grid, x="log_gdp", y="sqrt_cumulative", color="continent",
            color_discrete_map=color_map, size="bubble_size", size_max=60,
            animation_frame="month_str", animation_group="erez_moza",
            hover_name="erez_moza",
            hover_data={"continent": True, "fmt_cum": True, "fmt_monthly": True, "fmt_gdp": True,
                        "log_gdp": False, "sqrt_cumulative": False, "bubble_size": False, "month_str": False},
            labels={"log_gdp": "Log(GDP + 1)", "sqrt_cumulative": "Sqrt(Cumulative Immigrants)", "continent": ""},
            category_orders={"continent": all_continents}
        )

        # 2. Define custom hover template
        my_hover_template = (
            "<b>%{hovertext}</b><br>" +
            "<span style='font-size: 10px; color: #666;'>%{customdata[0]}</span><br><br>" +
            "סך העולים: <b>%{customdata[1]}</b><br>" +
            "עולים חודשיים: <b>%{customdata[2]}</b><br>" +
            "תל\"ג (שנתי): <b>%{customdata[3]}</b>" +
            "<extra></extra>"
        )
        
        # Apply hover template to the existing bubbles (Trace 0) BEFORE we add the text
        fig.update_traces(hovertemplate=my_hover_template, marker=dict(opacity=0.9, line=dict(width=1, color='DarkSlateGrey')))

        # 3. Calculate Position for Background Text
        # MOVED: Set to 0.5 (Center) instead of 0.02 (Left)
        text_x_pos = x_range[0] + (x_range[1] - x_range[0]) * 0.5
        text_y_pos = y_range[1] * 0.5
        
        # 4. Create the Background Text Trace
        background_text_trace = go.Scatter(
            x=[text_x_pos],
            y=[text_y_pos],
            text=[grid["month_str"].min()],
            mode="text",
            textfont=dict(size=160, color="rgba(200, 200, 200, 0.25)"), # Slightly transparent
            textposition="middle center", # Centers the text on the coordinates
            hoverinfo="skip", # CRITICAL: Ensures hovering the year doesn't break things
            showlegend=False
        )

        # 5. Add trace and Reorder safely to fix ValueError
        fig.add_trace(background_text_trace)
        # Move the last trace (text) to the front (index 0) so it is behind bubbles
        fig.data = fig.data[-1:] + fig.data[:-1]

        # 6. Update all Animation Frames
        for frame in fig.frames:
            # Create the text trace for this specific frame
            frame_text_trace = go.Scatter(
                x=[text_x_pos],
                y=[text_y_pos],
                text=[frame.name],
                mode="text",
                textfont=dict(size=160, color="rgba(200, 200, 200, 0.25)"),
                textposition="middle center",
                hoverinfo="skip",
                showlegend=False
            )
            # Insert text trace at index 0 for every frame to match fig.data
            frame.data = (frame_text_trace,) + frame.data
            
            # Re-apply hover template to bubbles (now at index 1)
            for trace in frame.data:
                if trace.mode != "text":
                    trace.hovertemplate = my_hover_template

        # 7. Configure Layout
        fig.update_layout(
            height=700, 
            margin=dict(l=20, r=20, t=90, b=130),
            xaxis=dict(range=x_range, title="""לוגריתם תל"ג"""),
            yaxis=dict(range=y_range, title="שורש כמות העולים המצטברת"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hoverlabel=dict(align="right")
        )

        # 8. Optimization: Enable smooth animation
        if fig.layout.updatemenus:
            btn = fig.layout.updatemenus[0].buttons[0]
            btn.args[1]["frame"]["duration"] = speed_ms
            btn.args[1]["transition"]["duration"] = max(0, int(speed_ms * 0.5))
            btn.args[1]["frame"]["redraw"] = False  # Smooth animation

        if fig.layout.sliders:
            fig.layout.sliders[0].currentvalue = {"visible": False}
            fig.layout.sliders[0].pad = {"t": 90}
            for step in fig.layout.sliders[0].steps:
                step["args"][1]["frame"]["redraw"] = False

        # Static annotation for Legend Title
        fig.add_annotation(
            text="<b>יבשות</b>",
            xref="paper", yref="paper",
            x=1.0, y=1.05,
            xanchor="right", yanchor="bottom",
            showarrow=False,
            font=dict(size=14)
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.checkbox("הצג טבלה", value=False):
            st.dataframe(grid)
# ==============================================================================
# PAGE 2: ISRAEL CITIES MAP (City Profiles)
# ==============================================================================
elif page == "מגמות קליטה לפי יישובים":

  st.set_page_config(layout="wide", page_title="מפת ערים ופרופילים דמוגרפיים", page_icon="🏙️")
  st.subheader("מפת ערים ופרופילים דמוגרפיים")

  # ==============================================================================
  # 1. STATE INITIALIZATION
  # ==============================================================================
  if 'selected_cities' not in st.session_state:
      st.session_state.selected_cities = []
  if 'last_map_select' not in st.session_state:
      st.session_state.last_map_select = []
  if 'previous_draw_order' not in st.session_state:
      st.session_state.previous_draw_order = []

  # --- MAP VIEW STATE ---
  # Default start view
  if 'map_view' not in st.session_state:
      st.session_state.map_view = {"lat": 31.6, "lon": 34.85, "zoom": 7.3}

  # ==============================================================================
  # 2. SELECTION LOGIC
  # ==============================================================================
  map_state = st.session_state.get("map_plot")
  if map_state and "selection" in map_state:
      current_map_points = [p['location'] for p in map_state['selection']['points']]
      if current_map_points != st.session_state.last_map_select:
          if len(current_map_points) == 1:
              clicked_id = current_map_points[0]
              if clicked_id in st.session_state.selected_cities:
                  st.session_state.selected_cities.remove(clicked_id)
              else:
                  st.session_state.selected_cities.append(clicked_id)
          elif len(current_map_points) > 1:
              st.session_state.selected_cities = list(set(st.session_state.selected_cities + current_map_points))

          st.session_state.last_map_select = current_map_points
          st.session_state.city_selector = st.session_state.selected_cities
          st.rerun()

  line_state = st.session_state.get("line_plot")
  if line_state and "selection" in line_state:
      points = line_state['selection']['points']
      if points:
          clicked_trace_index = points[0]['curveNumber']
          if st.session_state.previous_draw_order:
              if clicked_trace_index < len(st.session_state.previous_draw_order):
                  clicked_id = st.session_state.previous_draw_order[clicked_trace_index]
                  if clicked_id in st.session_state.selected_cities:
                      st.session_state.selected_cities.remove(clicked_id)
                  else:
                      st.session_state.selected_cities.append(clicked_id)

                  st.session_state.city_selector = st.session_state.selected_cities
                  del st.session_state["line_plot"]
                  st.rerun()

  # ==============================================================================
  # 3. DATA LOADING
  # ==============================================================================
  @st.cache_data
  def load_data():
      try:
          df = pd.read_csv(PAGE2_PATH)
          unique_ids = df['english_id'].unique()
          aggregated_rows = []
          for eid in unique_ids:
              group = df[df['english_id'] == eid]
              total_vol = group['total_olim'].sum()
              rep_name = group.sort_values('total_olim', ascending=False).iloc[0]['hebrew_name']
              avg_madad = group['madad'].mean() if 'madad' in group.columns else 0

              if total_vol > 0:
                  def w_avg(col): return (group[col] * group['total_olim']).sum() / total_vol
                  avg_age, pct_emp, pct_fem = w_avg('avg_age'), w_avg('pct_employed'), w_avg('pct_female')
              else:
                  avg_age, pct_emp, pct_fem = group['avg_age'].mean(), group['pct_employed'].mean(), group['pct_female'].mean()

              aggregated_rows.append({
                  'english_id': eid, 'hebrew_name': rep_name, 'total_olim': total_vol,
                  'avg_age': avg_age, 'pct_employed': pct_emp, 'pct_female': pct_fem,
                  'madad': avg_madad, 'score': group['score'].mean()
              })
          df_final = pd.DataFrame(aggregated_rows)
          df_final['log_total_olim'] = np.log10(df_final['total_olim'] + 1)

          np.random.seed(42)
          jitter_vals = np.random.uniform(-0.25, 0.25, size=len(df_final))
          df_final['madad_jittered'] = df_final['madad'] + jitter_vals
          return df_final.sort_values('hebrew_name')
      except Exception as e:
          st.error(f"Error loading data: {e}")
          st.stop()

  df_profile = load_data()
  try:
      with open(PATH_GEOJSON, "r", encoding="utf-8") as f:
          cities_geojson = json.load(f)
  except:
      st.error("Missing map file.")
      st.stop()

  id_to_name = pd.Series(df_profile.hebrew_name.values, index=df_profile.english_id).to_dict()
  dropdown_ids = df_profile['english_id'].tolist()

  # ==============================================================================
  # 4. CONTROLS
  # ==============================================================================
  def on_search_change():
      st.session_state.selected_cities = st.session_state.city_selector

  def on_reset_click():
      st.session_state.selected_cities = []
      st.session_state.city_selector = []
      st.session_state.last_map_select = []
      for key in ["map_plot", "line_plot"]:
          if key in st.session_state:
              del st.session_state[key]

  # --- VIEW CONTROLLER CALLBACK ---
  def set_view(lat, lon, zoom):
      st.session_state.map_view = {"lat": lat, "lon": lon, "zoom": zoom}

  c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([2, 0.5, 1.5])
  with c_ctrl1:
      # 1. Sync Logic: If the widget key doesn't exist yet, fill it from your saved data
      if 'city_selector' not in st.session_state:
          st.session_state.city_selector = st.session_state.selected_cities
      
      # 2. Widget: REMOVE "default=...". The widget automatically reads the value from 'key'
      st.multiselect(
          "בחר יישובים (חיפוש/סינון):",
          options=dropdown_ids,
          key='city_selector', # <--- This reads the value set in step 1
          on_change=on_search_change,
          format_func=lambda x: id_to_name.get(x, x),
          placeholder="כל הישובים (הקלד לחיפוש)"
      )

  with c_ctrl2:
      st.write(""); st.write("")
      st.button("🔄 איפוס", use_container_width=True, on_click=on_reset_click)
  with c_ctrl3:
      st.info("לחצו על אחד מהכפתורים מטה כדי לכוון את המפה לאזור מסוים")

  current_selection = st.session_state.selected_cities
  is_all_mode = (len(current_selection) == 0)

  # ==============================================================================
  # 5. CUSTOM PLOT CONFIGURATION
  # ==============================================================================
  features = [
      {'label': 'גיל ממוצע', 'col': 'avg_age', 'plot_col': 'avg_age', 'suffix': ''},
      {'label': 'מדד', 'col': 'madad', 'plot_col': 'madad_jittered', 'suffix': ''},
      {'label': '% תעסוקה', 'col': 'pct_employed', 'plot_col': 'pct_employed', 'suffix': '%'},
      {'label': '% נשים', 'col': 'pct_female', 'plot_col': 'pct_female', 'suffix': '%'},
  ]
  ranges = {}
  for f in features:
      ranges[f['col']] = {
          'min_real': df_profile[f['col']].min(), 'max_real': df_profile[f['col']].max(),
          'min_plot': df_profile[f['plot_col']].min(), 'max_plot': df_profile[f['plot_col']].max()
      }

  
  
  log_min, log_max = df_profile['log_total_olim'].min(), df_profile['log_total_olim'].max()

  def get_amp_color(value, vmin, vmax, opacity=1.0):
      # 1. Normalize the value (0 to 1)
      norm_val = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
      
      # 2. Sample the "Amp" scale at this normalized point
      # sample_colorscale returns a list of strings, we take the first one
      color_string = sample_colorscale("Amp", [norm_val])[0]
      
      # 3. Convert to RGBA to handle opacity
      # Plotly usually returns 'rgb(r, g, b)' or hex. We handle both.
      if color_string.startswith("rgb"):
          return color_string.replace("rgb", "rgba").replace(")", f", {opacity})")
      elif color_string.startswith("#"):
          # Convert hex to rgba
          h = color_string.lstrip('#')
          r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
          return f"rgba({r}, {g}, {b}, {opacity})"
      return color_string


  # ==============================================================================
  # 6. PLOT LOGIC
  # ==============================================================================
  traces, annotations, shapes = [], [], []
  x_labels = [f['label'] for f in features]

  if is_all_mode:
      draw_order = df_profile['english_id'].tolist()
  else:
      bg_ids = [x for x in df_profile['english_id'] if x not in current_selection]
      fg_ids = [x for x in df_profile['english_id'] if x in current_selection]
      draw_order = bg_ids + fg_ids

  st.session_state.previous_draw_order = draw_order

  for eid in draw_order:
      row = df_profile[df_profile['english_id'] == eid].iloc[0]
      is_selected = (eid in current_selection) or is_all_mode

      if is_all_mode:
          # CHANGE HERE: Use get_amp_color instead of get_mpl_color
          line_color = get_amp_color(row['log_total_olim'], log_min, log_max, opacity=0.35)
          line_width = 1.5; hover_info = 'text'
          htemplate = f"<b>{row['hebrew_name']}</b><br>מדד: {row['madad']:.2f}<br>עולים: {int(row['total_olim']):,}<extra></extra>"
      else:
          if is_selected:
              # CHANGE HERE: Use get_amp_color instead of get_mpl_color
              line_color = get_amp_color(row['log_total_olim'], log_min, log_max, opacity=1.0)
              line_width = 4.0; hover_info = 'text'
              htemplate = f"<b>{row['hebrew_name']}</b><br>מדד: {row['madad']:.2f}<br>עולים: {int(row['total_olim']):,}<extra></extra>"
          else:
              line_color = 'rgba(200, 200, 200, 0.05)'; line_width = 1.0; hover_info = 'skip'; htemplate = None

      y_vals, hover_texts = [], []
      for f in features:
          r = ranges[f['col']]
          val_plot = row[f['plot_col']]; val_real = row[f['col']]
          norm = 0.5 if r['max_plot'] == r['min_plot'] else (val_plot - r['min_plot']) / (r['max_plot'] - r['min_plot'])
          y_vals.append(norm)
          hover_texts.append(f"{val_real:.1f}{f['suffix']}")

      traces.append(go.Scatter( #TODO
          x=x_labels, y=y_vals, mode='lines',
          line=dict(color=line_color, width=line_width),
          name=row['hebrew_name'], text=hover_texts, hovertemplate=htemplate,
          showlegend=False, hoverinfo=hover_info
      ))

  def get_nice_ticks(min_v, max_v):
      if min_v == max_v: return [min_v]
      target_ticks = np.linspace(min_v, max_v, 5)
      nice_ticks = []
      for t in target_ticks:
          if abs(t) >= 10: nice_ticks.append(int(round(t)))
          elif abs(t) >= 1: nice_ticks.append(round(t, 1))
          else: nice_ticks.append(round(t, 2))
      return sorted(list(set(nice_ticks)))

  for i, f in enumerate(features):
      r = ranges[f['col']]
      shapes.append(dict(type="line", x0=i, x1=i, y0=-0.05, y1=1.05, line=dict(color="gray", width=1.5), xref="x", yref="y"))
      ticks = get_nice_ticks(r['min_real'], r['max_real'])
      for t in ticks:
          if r['max_real'] == r['min_real']: y_pos = 0.5
          else: y_pos = (t - r['min_plot']) / (r['max_plot'] - r['min_plot'])
          annotations.append(dict(x=i, y=y_pos, text=f"– {t}{f['suffix']}", showarrow=False, xanchor="left", font=dict(size=12, color="black", weight="bold"), xref='x', yref='y', xshift=2))
      annotations.append(dict(x=i, y=1.1, text=f"<b>{f['label']}</b>", showarrow=False, font=dict(size=13, color="black"), xref='x', yref='y'))

  fig_lines = go.Figure(data=traces)
  fig_lines.update_layout(
      title="השוואת מדדים (ניתן ללחוץ על קו לבחירה)",
      xaxis=dict(showgrid=False, showticklabels=False, range=[-0.2, len(features)-0.5]),
      yaxis=dict(showgrid=False, showticklabels=False, range=[-0.1, 1.15]),
      margin=dict(l=20, r=20, b=20, t=60), height=500, hovermode='closest', annotations=annotations, shapes=shapes, plot_bgcolor='white', dragmode=False
  )

  # ==============================================================================
  # 7. MAP RENDER
  # ==============================================================================
  df_reset = df_profile.reset_index(drop=True)
  selected_indices = None
  if not is_all_mode:
      selected_indices = df_reset.index[df_reset['english_id'].isin(current_selection)].tolist()

  fig_map = go.Figure(go.Choroplethmapbox( 
      geojson=cities_geojson, locations=df_reset['english_id'], featureidkey="id",
      z=df_reset['log_total_olim'],
      colorscale='Amp', #trying amp
      zmin=log_min, zmax=log_max,
      marker_opacity=1.0,
      marker_line_width=1, marker_line_color='white',
      text=df_reset['hebrew_name'], customdata=df_reset['total_olim'],
      hovertemplate="<b>%{text}</b><br>סה\"כ עולים: %{customdata:,}<extra></extra>",
      showscale=True, #TODO to show the spectrum
      colorbar=dict(title="סקאלת עולים", orientation="h", y=-0.15, thickness=15),
      selectedpoints=selected_indices,
      selected=dict(marker=dict(opacity=1.0)),
      unselected=dict(marker=dict(opacity=0.4))
  ))

  fig_map.update_layout(
      mapbox_style="carto-positron",
      # Use Dynamic View State
      mapbox_center={"lat": st.session_state.map_view["lat"], "lon": st.session_state.map_view["lon"]},
      mapbox_zoom=st.session_state.map_view["zoom"],
      margin={"r":0,"t":30,"l":0,"b":0}, height=500, clickmode='event+select', title="מפת עולים"
  )

  # DISPLAY
  c1, c2 = st.columns([1.5, 1])
  with c1:
      st.plotly_chart(fig_lines, use_container_width=True, on_select="rerun", key="line_plot", selection_mode="points")
  with c2:
      # --- 4 ZOOM BUTTONS ---
      b1, b2, b3, b4 = st.columns(4)
      with b1:

          st.button("דרום", on_click=set_view, args=(30.2, 35.1, 6.7), use_container_width=True)
      with b2:
          # North: Zoomed OUT from 8.5 -> 7.8
          st.button("מרכז", on_click=set_view, args=(31.95, 35.05, 8.2), use_container_width=True)
      with b3:
          # Center: Zoomed OUT and shifted LEFT (West)
          st.button("צפון", on_click=set_view, args=(32.9, 35.3, 7.8), use_container_width=True)
      with b4:
          # South: Zoomed OUT A LOT and shifted RIGHT (East)
          st.button("כל ישראל", on_click=set_view, args=(31.4, 35.0, 5.8), use_container_width=True)

      st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", key="map_plot", selection_mode="points")

  # ==============================================================================
  # 8. DYNAMIC DATA TABLE
  # ==============================================================================
  if not is_all_mode:
      st.divider()
      st.markdown("### 📋 נתוני ערים נבחרות")
      selected_data = df_profile[df_profile['english_id'].isin(current_selection)].copy()
      cols_to_show = ['hebrew_name', 'avg_age', 'madad', 'pct_employed', 'pct_female', 'total_olim']
      rename_map = {'hebrew_name': 'שם הישוב', 'avg_age': 'גיל ממוצע', 'madad': 'מדד', 'pct_employed': '% תעסוקה', 'pct_female': '% נשים', 'total_olim': 'סה"כ עולים'}
      table_display = selected_data[cols_to_show].rename(columns=rename_map)
      st.dataframe(table_display.style.format({'גיל ממוצע': "{:.1f}", 'מדד': "{:.2f}", '% תעסוקה': "{:.1f}%", '% נשים': "{:.1f}%", 'סה"כ עולים': "{:,.0f}"}), use_container_width=True, hide_index=True)


# ==============================================================================
# PAGE 3: PROFESSIONAL FLOW (SANKEY)
# ==============================================================================
elif page == "תחומי תעסוקה של עולים לפי מדינת מוצא":
    
    # --- 1. CSS: Scoped RTL (Main content only) ---
    st.markdown("""
        <style>
        [data-testid="stMain"] h1, 
        [data-testid="stMain"] h2, 
        [data-testid="stMain"] h3, 
        [data-testid="stMain"] h4, 
        [data-testid="stMain"] h5, 
        [data-testid="stMain"] h6, 
        [data-testid="stMain"] p, 
        [data-testid="stMain"] .stCaption {
            text-align: right !important;
            direction: rtl !important;
        }

        [data-testid="stMain"] .stMultiSelect label, 
        [data-testid="stMain"] .stButton button {
            text-align: right !important;
            direction: rtl !important;
            width: 100%;
        }
        
        [data-testid="stMain"] div[data-baseweb="select"] {
            direction: rtl;
        }

        .modebar {
            left: 0 !important;
            right: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("זרימת עולים: מארץ מוצא לתחום עיסוק")
    st.caption("תרשים זרימה המציג את המעבר בין מדינות המוצא לקבוצות מקצועיות (לאחר איחוד קטגוריות).")

    # 1. Load Data
    @st.cache_data
    def load_sankey_data(path):
        df = pd.read_csv(path)
        return df

    df_sankey = load_sankey_data(PAGE3_PATH) 

    # 2. Controls - Country Selection
    country_totals = df_sankey.groupby('erez_moza')['count'].sum()
    top_4_countries = country_totals.nlargest(4).index.tolist()
    all_countries_available = df_sankey['erez_moza'].unique().tolist()
    
    sorted_options = top_4_countries + [c for c in all_countries_available if c not in top_4_countries]

    if 'country_selector' not in st.session_state:
        st.session_state['country_selector'] = top_4_countries

    def select_all():
        st.session_state['country_selector'] = sorted_options

    def deselect_all():
        st.session_state['country_selector'] = []
    def select_top4():
        st.session_state['country_selector'] = top_4_countries

    # --- Button Layout ---
    # Changed columns to make room for the 3rd button
    # [Spacer, Top 4, Select All, Deselect All]
    col1, col2, col3, col4 = st.columns([5, 1.5, 1.5, 1.5]) 
    
    with col1:
        st.empty() 
    with col2:
        # NEW: Button for Top 4
        st.button("4 המובילות", on_click=select_top4, use_container_width=True)
    with col3:
        st.button("בחר הכל", on_click=select_all, use_container_width=True)
    with col4:
        st.button("נקה בחירה", on_click=deselect_all, use_container_width=True)

    selected_countries = st.multiselect(
        "בחר מדינות להצגה:",
        options=sorted_options,
        key='country_selector' 
    )

    if not selected_countries:
        st.warning("אנא בחר לפחות מדינה אחת להצגה.")
        st.stop()

    # 3. Filter Data
    flows = df_sankey[df_sankey['erez_moza'].isin(selected_countries)].copy()
    
    # 4. Prepare Sankey Data
    unique_countries = selected_countries
    unique_subjects = flows['subject'].unique().tolist()
    all_labels = unique_countries + unique_subjects

    # Formatted Labels
    styled_labels = []
    for label in all_labels:
        styled_labels.append(f"<span style='background-color:rgba(255,255,255,0.8); color:black;'><b>{label}</b></span>")

    label_map = {label: i for i, label in enumerate(all_labels)}

    source_indices = flows['erez_moza'].map(label_map)
    target_indices = flows['subject'].map(label_map)
    values = flows['count']

    # 5. Coloring Logic
    color_palette = px.colors.qualitative.Bold 
    country_color_map = {
        country: color_palette[i % len(color_palette)] 
        for i, country in enumerate(unique_countries)
    }

    def get_rgba_string(color_val, opacity):
        if color_val.startswith('rgb'):
            if 'rgba' in color_val:
                return color_val 
            else:
                return color_val.replace('rgb', 'rgba').replace(')', f', {opacity})')
        else:
            try:
                rgba = mcolors.to_rgba(color_val, alpha=opacity)
                return f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3]})'
            except:
                return f'rgba(128, 128, 128, {opacity})'

    node_colors = [country_color_map[label] if label in country_color_map else "lightgrey" for label in all_labels]
    link_colors = [get_rgba_string(country_color_map[row['erez_moza']], 0.4) for _, row in flows.iterrows()]

    # 6. Create Plot
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=styled_labels,
            color=node_colors,
            # Node Hover: Added <span style='color:black'> to force the number to match the text
            hovertemplate='<b>%{label}</b><br>כמות: <span style="color:black"><b>%{value:,.0f}</b></span><extra></extra>',
            align='right' 
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors,
            # Link Hover: Added <span style='color:black'> to force the number to match the text
            hovertemplate=(
                'מדינת מוצא: <b>%{source.label}</b>' + 
                '<br>' + 
                'מקצוע: <b>%{target.label}</b>' + 
                '<br>' + 
                'כמות: <span style="color:black"><b>%{value:,.0f}</b></span><extra></extra>'
            )
        )
    )])

    fig.update_layout(
        title=dict(
            text="<b>התפלגות מקצועות לפי מדינות מוצא</b>",
            x=1,            
            xanchor='right' 
        ),
        title_font_size=20,
        font=dict(family="Arial, sans-serif", size=14, color="black"),
        plot_bgcolor='white',
        height=700,
        margin=dict(l=10, r=10, t=50, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)
