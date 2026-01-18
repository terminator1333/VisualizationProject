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

# -------------------------
# Page setup
# -------------------------
st.set_page_config(page_title="Israel Data Dashboard", page_icon="🇮🇱", layout="wide")

# -------------------------
# Navigation
# -------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["מגמות עלייה ממדינות מוצא", "מגמות קליטה לפי יישובים", "תחומי תעסוקה של עולים לפי מדינת מוצא"]) #all the pages

# -------------------------
# Configuration
# -------------------------

PATH_GEOJSON = "/datasets/israel_map.geojson"

PAGE1_PATH = "/datasets/page1_final.csv"

PAGE2_PATH = "/datasets/page2_final.csv"

PAGE3_PATH = "/datasets/page3_final.csv"

# ==============================================================================
# PAGE 1: IMMIGRATION TRENDS
# ==============================================================================
if page == "מגמות עלייה ממדינות מוצא":

    col_header_1, col_header_2 = st.columns([4, 1])
    with col_header_1:
        st.title("עלייה לאורך השנים")
    with col_header_2:
        st.markdown("### 🌍✈️✡️")
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

    st.markdown("### Filters")
    c1, c2, c3 = st.columns([2, 2, 3])

    min_date = df_merged["date"].min()
    max_date = df_merged["date"].max()

    with c1:
        year_range = st.slider(
            "Year Range",
            int(min_date.year),
            int(max_date.year),
            (int(min_date.year), int(max_date.year))
        )

    with c2:
        speed_ms = st.slider("Animation Speed (ms)", 50, 500, 100, step=10)

    with c3:
        all_continents = sorted(df_merged["continent"].unique())
        selected_continents = st.multiselect("Continents", all_continents, default=all_continents)

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
        st.warning("No immigration data found.")
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
        st.markdown("#### Select Countries")

        country_stats = base_filtered.groupby("erez_moza")["monthly_count"].sum().sort_values(ascending=False)
        all_countries_sorted = sorted(base_filtered["erez_moza"].unique())
        default_top_25 = set(country_stats.index.tolist()[:25])

        for country in all_countries_sorted:
            key = f"chk_{country}"
            if key not in st.session_state:
                st.session_state[key] = country in default_top_25

        search_query = st.text_input("Search Country", "", placeholder="Type to filter...")
        visible_countries = [c for c in all_countries_sorted if search_query.lower() in c.lower()]

        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("Select All"):
            for country in visible_countries: st.session_state[f"chk_{country}"] = True
            st.rerun()
        if btn_col2.button("Deselect All"):
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
            base_choropleth = px.choropleth(
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
        fig = px.scatter(
            grid, x="log_gdp", y="sqrt_cumulative", color="continent",
            color_discrete_map=color_map, size="bubble_size", size_max=60,
            animation_frame="month_str", animation_group="erez_moza",
            hover_name="erez_moza",
            hover_data={"continent": True, "fmt_cum": True, "fmt_monthly": True, "fmt_gdp": True,
                        "log_gdp": False, "sqrt_cumulative": False, "bubble_size": False, "month_str": False},
            labels={"log_gdp": "Log(GDP + 1)", "sqrt_cumulative": "Sqrt(Cumulative Immigrants)"},
            category_orders={"continent": all_continents}
        )

        my_hover_template = (
            "<b>%{hovertext}</b><br>" +
            "<span style='font-size: 10px; color: #666;'>%{customdata[0]}</span><br><br>" +
            "Total Immigrants: <b>%{customdata[1]}</b><br>" +
            "Monthly Immigrants: <b>%{customdata[2]}</b><br>" +
            "GDP (Annualized): <b>%{customdata[3]}</b>" +
            "<extra></extra>"
        )
        fig.update_traces(hovertemplate=my_hover_template, marker=dict(opacity=0.9, line=dict(width=1, color='DarkSlateGrey')))

        if fig.frames:
            for frame in fig.frames:
                if frame.data:
                    for trace in frame.data:
                        trace.hovertemplate = my_hover_template

        fig.update_layout(
            height=700, margin=dict(l=20, r=20, t=40, b=130),
            xaxis=dict(range=x_range, title="""לוגריתם תל"ג"""),
            yaxis=dict(range=y_range, title="שורש כמות העולים המצטברת"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        text_style = dict(
            xref="paper", yref="paper", x=0.01, y=0.99,
            xanchor="left", yanchor="top", showarrow=False,
            font=dict(size=160, color="rgba(160, 160, 160, 0.35)")
        )
        first_date = grid["month_str"].min()
        fig.add_annotation(text=first_date, **text_style)

        if fig.frames:
            for frame in fig.frames:
                frame.layout.annotations = [dict(text=frame.name, **text_style)]

        if fig.layout.updatemenus:
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = speed_ms
            fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = max(0, int(speed_ms * 0.35))
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = True

        if fig.layout.sliders:
            fig.layout.sliders[0].currentvalue = {"visible": False}
            fig.layout.sliders[0].pad = {"t": 90}
            for step in fig.layout.sliders[0].steps:
            # step["args"][1] is the animation config for that specific step.
            # We set redraw=True to force the background text (annotation) to update.
                step["args"][1]["frame"]["redraw"] = True

        st.plotly_chart(fig, use_container_width=True)

        if st.checkbox("Show Data Table", value=False):
            st.dataframe(grid)


# ==============================================================================
# PAGE 2: ISRAEL CITIES MAP (City Profiles)
# ==============================================================================
elif page == "מגמות קליטה לפי יישובים":

  st.set_page_config(layout="wide", page_title="Israel Demographics")
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
      with open(r"C:\Users\user\Downloads\israel_map.geojson", "r", encoding="utf-8") as f:
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
      st.multiselect("בחר יישובים (חיפוש/סינון):", options=dropdown_ids, key='city_selector', on_change=on_search_change, format_func=lambda x: id_to_name.get(x, x), placeholder="כל הישובים (הקלד לחיפוש)")
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

  # --- SHADED MATPLOTLIB LOGIC ---
  log_min, log_max = df_profile['log_total_olim'].min(), df_profile['log_total_olim'].max()

  try:
      mpl_cmap = matplotlib.colormaps['jet']
  except:
      mpl_cmap = cm.get_cmap('jet')

  SHADING_FACTOR = 0.7

  def apply_shading(rgb_tuple, factor):
      h, s, v = colorsys.rgb_to_hsv(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
      v = v * factor
      return colorsys.hsv_to_rgb(h, s, v)

  def get_mpl_color(value, vmin, vmax, opacity=1.0):
      norm_val = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.5
      rgba = mpl_cmap(norm_val)
      shaded_rgb = apply_shading(rgba[:3], SHADING_FACTOR)
      return f"rgba({int(shaded_rgb[0]*255)}, {int(shaded_rgb[1]*255)}, {int(shaded_rgb[2]*255)}, {opacity})"

  def mpl_to_plotly_scale(cmap, steps=255):
      scale = []
      for i in range(steps + 1):
          norm = i / steps
          rgba = cmap(norm)
          shaded_rgb = apply_shading(rgba[:3], SHADING_FACTOR)
          color_string = f"rgb({int(shaded_rgb[0]*255)}, {int(shaded_rgb[1]*255)}, {int(shaded_rgb[2]*255)})"
          scale.append([norm, color_string])
      return scale

  plotly_jet_scale = mpl_to_plotly_scale(mpl_cmap)


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
          line_color = get_mpl_color(row['log_total_olim'], log_min, log_max, opacity=0.35)
          line_width = 1.5; hover_info = 'text'
          htemplate = f"<b>{row['hebrew_name']}</b><br>מדד: {row['madad']:.2f}<br>עולים: {int(row['total_olim']):,}<extra></extra>"
      else:
          if is_selected:
              line_color = get_mpl_color(row['log_total_olim'], log_min, log_max, opacity=1.0)
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

      traces.append(go.Scatter(
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
      colorscale=plotly_jet_scale,
      zmin=log_min, zmax=log_max,
      marker_opacity=1.0,
      marker_line_width=1, marker_line_color='white',
      text=df_reset['hebrew_name'], customdata=df_reset['total_olim'],
      hovertemplate="<b>%{text}</b><br>סה\"כ עולים: %{customdata:,}<extra></extra>",
      showscale=True,
      colorbar=dict(title="סקאלת עולים (לוגריתמי)", orientation="h", y=-0.15, thickness=15),
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

    selected_countries = st.multiselect(
        "בחר מדינות להצגה:",
        options=sorted_options,
        default=top_4_countries
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

    # Create Indices
    # We use the selected countries list directly (Source)
    unique_countries = selected_countries 
    # We use ONLY subjects present in the filtered, mapped flows (Target)
    unique_subjects = flows['subject'].unique().tolist()

    all_labels = unique_countries + unique_subjects
    
    # --- FORMATED LABELS
    # Instead of moving text, we use HTML to give it a background color.
    # This guarantees readability regardless of where Plotly places the node.
    styled_labels = []
    for label in all_labels:
        # white background (0.8 opacity), black text, bold
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
            thickness=30, # Thick nodes help visual separation
            line=dict(color="black", width=0.5),
            label=styled_labels, # Use the HTML styled labels
            color=node_colors,
            hovertemplate='<b>%{label}</b><br>כמות: %{value}<extra></extra>'
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors,
            hovertemplate='<b>%{source.label}</b> ← <b>%{target.label}</b><br>כמות: %{value}<extra></extra>'
        )
    )])

    fig.update_layout(
        title_text="<b>התפלגות מקצועות לפי מדינות מוצא</b>",
        title_font_size=20,
        font=dict(family="Arial, sans-serif", size=14, color="black"),
        plot_bgcolor='white',
        height=700,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
