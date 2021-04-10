import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from pathlib import Path
from SessionState import get




# def read_markdown_file(markdown_file):
#     return Path(markdown_file).read_text()

# ### FUNCTIONS TO LOAD SAVED DATA AND/OR CLUSTERING RESULTS

# @st.cache(allow_output_mutation=True)
# def get_mech_data():
#     df = pd.read_csv("cleaned_data/clusters_by_mech_props.csv")
#     return df.set_index("Material Name")

# @st.cache(allow_output_mutation=True)
# def get_pca_data():
#     df = pd.read_csv("cleaned_data/pca_data.csv")
#     return df.set_index("Material Name")

# # compute weighted cost of blends given their fiber constituents
# # and a dictionary containing the cost of staple fibers
# def weighted_cost(cost, fibers):
#     try:
#         costs = [cost[f] for f in eval(fibers)]
#         return sum(costs)/len(costs)
#     except:
#         print(fibers)

# # read in higg data and do some cleaning and preprocessing
# @st.cache(allow_output_mutation=True)
# def get_higg_data():
#     df = pd.read_csv("cleaned_data/higg_mapped.csv")
#     df.drop(columns=["Material Score", "Material Constituent"], inplace=True)
#     df.rename(columns={"Global Warming Score": "Global Warming", "Eutrophication Score": "Eutrophication", "Water Scarcity Score": "Water Scarcity", "Abiotic Resource Depletion, Fossil Fuels Score": "Fossil Fuels Score", "Biogenic Carbon Content (kg C)": "Biogenic Carbon Content", "Water Consumption (kg)": "Water Consumption"}, inplace=True)
#     return df

# # a debugging function to make sure the higg data looks good
# def higg_dataframe(df):
#     data = df
#     st.write("### Environmental Properties using Higg Methodology", data.sort_index())

# # the heart of the app
# def main():
#     # session state authentication to make it password-protected
#     session_state = get(password='')
#     authenticated = False
#     if session_state.password == 'SustainableTextiles!':
#         authenticated = True
#     if session_state.password != 'SustainableTextiles!':
#         pwd_placeholder = st.sidebar.empty()
#         pwd = pwd_placeholder.text_input("Password:", value="", type="password")
#         session_state.password = pwd
#         if session_state.password == 'SustainableTextiles!':
#             session_state.auth = True
#             authenticated = True

#     # load in mechanical data, clustering results, and environmental scores
#     mech = get_mech_data()
#     pca = get_pca_data()
#     higg = get_higg_data()

#     # select page on left sidebar
#     page = st.sidebar.selectbox("Choose a page", ["Homepage", "Mechanical", "Environmental"])

#     # only display content if valid password has been provided
#     if authenticated == True:
#         # an overview of the tool for new users
#         if page == "Homepage":
#             st.title("Sustainable Substitutes for Natural and Synthetic Textiles: An Algorithmic Clustering Approach")
#             st.header("Project Overview")
#             st.markdown("**Summary**: This web application serves as a tool for designers to make more environmentally-conscious decisions when developing products.")
#             st.markdown("**Purpose**: Suggest more sustainable textile alternatives that possess similar mechanical properties to the user-inputted fabric or fiber.")
#             st.markdown("**Approach**:  \n1. Apply K-Means Clustering with PCA to divide 23 different fiber constituents into groups with similar physical characteristics.  \n2. Use a naive fiber to textile mapping, filter the textile variants by the mechanically similar group of interest.  \n3. Suggest the most sustainable textile variants in the group of interest using a weighted sum of Higg Materials Sustainability Index components based on the relative importance the user places on each metric of environmental impact.")
#             st.markdown("**Target user**: a materials developer who is looking to select a textile for a sustainable product.")
#             st.markdown("**Mechanical Features**: The mechanical properties of the synthetic and natural fiber constituents that we explored include density, tenacity, elongation, initial modulus, and moisture regain. These were compiled and cross-referenced from a few different papers which are cited in our paper.")
#             mech_features = st.checkbox("Click this to learn more about the mechanical features")
#             if mech_features:
#                 st.markdown(read_markdown_file("./definitions/mech_features.md"), unsafe_allow_html=True)
#             st.markdown("**Environmental Features**: The Higg Materials Sustainability Index (MSI) is a weighted sum comprised of 7 different environmental impact scores, where lower scores imply more sustainable materials.")
#             env_features = st.checkbox("Click this to learn more about the environmental features")
#             if env_features:
#                 st.markdown(read_markdown_file("./definitions/env_features.md"), unsafe_allow_html=True)

#         # visualizations of mechanical properties and clustering results
#         elif page == "Mechanical":
#             st.title("Mechanical Properties: K-Means Clustering with PCA")
#             cluster_dataframe(mech)
#             x_axis = list(mech.index)
#             y_axis = st.selectbox("Choose a variable for the y-axis", list(mech.columns)[:-1], index=3)
#             visualize_data(mech, x_axis, y_axis)
#             visualize_clusters(pca)

#         # top suggestions by environmental scores
#         elif page == "Environmental":
#             st.title("Sustainable Alternatives: Environmentally-friendly Suggestions by Weighted Sum")
#             fiber_options = get_set_intersection(mech, higg)
#             fiber = fiber_selection(fiber_options)
#             initial_material = higg_material_selection(fiber, higg)
#             filtered_df = filter_by_fiber_cluster(fiber, mech, higg)
#             best_material, best_fiber = get_suggestions(filtered_df)
#             normalized_env = make_normalized_df(filtered_df, 2)
#             env_radar_chart(normalized_env, initial_material, best_material)
#             normalized_mech = make_normalized_df(mech.drop(columns="Cluster").reset_index(), 1)
#             initial_fiber = fiber if "BL" not in initial_material else None
#             if initial_fiber and best_fiber:
#                 mech_radar_chart(normalized_mech, fiber, best_fiber)
#     else:
#         st.write("Please login to use the tool.")

# # filter the mechanical dataframe by clusters of interest
# def cluster_dataframe(df):
#     clusters = st.multiselect(
#         "Choose a cluster", list(sorted(df["Cluster"].unique())), [0,1]
#     )
#     if not clusters:
#         st.error("Please select at least one cluster.")
#         return

#     data = df.loc[df['Cluster'].isin(clusters)]
#     st.write("### Mechanical Properties by Fiber Constituents", data.sort_index())

# # visualize the fiber constituents by specified mechanical property, 
# # color-coded by cluster groupings
# def visualize_data(df, x_axis, y_axis):
#     graph = alt.Chart(df.reset_index()).mark_bar().encode(
#         x=alt.X('Material Name', sort='y'),
#         y=alt.Y(str(y_axis)+":Q"),
#         color='Cluster'
#     ).interactive()
#     st.altair_chart(graph, use_container_width=True)

# # visualize component 1 vs. component 2 after clustering has been performed
# def visualize_clusters(df):
#     graph = alt.Chart(df.reset_index()).mark_circle(size=60).encode(
#         x=alt.X('Component 2'),
#         y=alt.Y('Component 1'),
#         color=alt.Color('Cluster', scale=alt.Scale(scheme='category20b')),
#         tooltip=['Material Name']
#     ).interactive()
#     st.altair_chart(graph, use_container_width=True)

# # naive mapping to filter higg data by fiber constituents in cluster of interest
# @st.cache()
# def get_set_intersection(mech_df, higg_df):
#     fiber_options = []
#     for fibers in higg_df["Fiber Constituent(s)"]:
#         for fiber in eval(fibers):
#             if fiber not in fiber_options and fiber in mech_df.index:
#                 print(fiber)
#                 fiber_options.append(fiber)
#     return sorted(fiber_options)

# # have user select an initial / intended fiber to use in a product
# def fiber_selection(fiber_options):
#     fiber = st.selectbox("Choose a fiber", fiber_options)
#     while not fiber:
#         st.error("Please select a fiber.")
#     return fiber

# # select a higg material containing the inputted fiber
# # note: this is initially random, but the user can select a specific higg material
# def higg_material_selection(fiber, higg_df):
#     higg_fiber = higg_df.iloc[[i for i, fibers in enumerate(higg_df["Fiber Constituent(s)"]) if fiber in eval(fibers)]]
#     material_list = [mat for mat in list(higg_fiber["Material Name"])]
#     material = st.selectbox("Now please select a Higg textile containing that fiber", material_list)
#     while not material:
#         st.error("Please select a material.")
#     return material

# # filter the higg data by the fibers in the cluster of interest
# def filter_by_fiber_cluster(fiber, mech_df, higg_df):
#     mech_df = mech_df.reset_index()
#     cluster = int(mech_df.loc[mech_df["Material Name"] == fiber]["Cluster"])
#     similar = mech_df.loc[mech_df["Cluster"] == cluster]
#     st.write("### Similar Fiber Consituents", similar)
#     in_cluster = [i for i, fibers in enumerate(higg_df["Fiber Constituent(s)"]) if len(set(eval(fibers)).intersection(set(similar["Material Name"]))) > 0]
#     return higg_df.iloc[in_cluster]

# # make an environmental radar chart of the initial material and top suggestion
# def env_radar_chart(normalized_df, initial_material, best_material):
#     initial = normalized_df.loc[normalized_df["Material Name"] == initial_material]
#     best = normalized_df.loc[normalized_df["Material Name"] == best_material]
#     fig = go.Figure()
#     fig.add_trace(go.Scatterpolar(
#         r=list(initial[initial.columns[2:]].iloc[0]),
#         theta=initial.columns[2:],
#         fill='toself',
#         name=initial_material + ": " + ", ".join(eval(initial["Fiber Constituent(s)"].iloc[0]))
#     ))
#     fig.add_trace(go.Scatterpolar(
#         r=list(best[best.columns[2:]].iloc[0]),
#         theta=best.columns[2:],
#         fill='toself',
#         name=best_material + ": " + ", ".join(eval(best["Fiber Constituent(s)"].iloc[0]))
#     ))
#     fig.update_layout(
#     polar=dict(
#         radialaxis=dict(
#         visible=True,
#         range=[0, 1]
#         )),
#     showlegend=True
#     )
#     st.write("### Environmental Property Radar Chart (initial vs. suggested)", fig)

# # make an environmental radar chart of the initial material and top suggestion
# # NOTE: if the top suggestion is a blend, do not infer mechanical properties
# # the user should verify that the top suggestion meets functional needs
# def mech_radar_chart(mech_df, initial_fiber, best_fiber):
#     initial = mech_df.loc[mech_df["Material Name"] == initial_fiber]
#     best = mech_df.loc[mech_df["Material Name"] == best_fiber]
#     fig = go.Figure()
#     fig.add_trace(go.Scatterpolar(
#         r=list(initial[initial.columns[1:]].iloc[0]),
#         theta=initial.columns[1:],
#         fill='toself',
#         name=initial_fiber
#     ))
#     fig.add_trace(go.Scatterpolar(
#         r=list(best[best.columns[1:]].iloc[0]),
#         theta=best.columns[1:],
#         fill='toself',
#         name=best_fiber
#     ))
#     fig.update_layout(
#     polar=dict(
#         radialaxis=dict(
#         visible=True,
#         range=[0, 1]
#         )),
#     showlegend=True
#     )
#     st.write("### Mechanical Property Radar Chart (initial vs. suggested)\n NOTE: performance properties will not be inferred if the material is a blend", fig)

# # super simple function to apply user weights of environmental features 
# # as coefficients in weighted score
# def get_weighted_score(coeffs, row):
#     return sum([coeffs[i] * val for i, val in enumerate(row)])

# # get top 5 lowest weighted scores and output them as top suggestions
# def get_suggestions(df):
#     st.write("### Cluster-specific Materials with Higg Environmental Properties", df)
#     non_features = df[df.columns[:2]]
#     env_features = df[df.columns[2:]]
#     coeffs = [st.sidebar.select_slider(col, [float(i)/100 for i in range(101)], float(1)) for col in env_features.columns]
#     norm = MinMaxScaler().fit_transform(env_features)
#     scaled_env = pd.DataFrame(norm, index=df.index)
#     non_features['Weighted Score'] = scaled_env.apply(lambda row: get_weighted_score(coeffs, list(row)), axis=1)
#     top_suggestions = non_features.sort_values(by='Weighted Score')
#     st.write("### Sustainable Alternatives by Lowest Weighted Score", top_suggestions.head(5))
#     best_material = str(top_suggestions.reset_index().iloc[0, 1])
#     if len(eval((top_suggestions.reset_index().iloc[0, 2]))) == 1:
#         best_fiber = eval((top_suggestions.reset_index().iloc[0, 2]))[0]
#     else:
#         best_fiber = None
#     print(best_material, best_fiber)
#     return best_material, best_fiber

# # normalize any dataframe if values need to be between 0 and 1
# @st.cache(allow_output_mutation=True)
# def make_normalized_df(df, col_sep):
#     non_features = df[df.columns[:col_sep]]
#     features = df[df.columns[col_sep:]]
#     norm = MinMaxScaler().fit_transform(features)
#     scaled = pd.DataFrame(norm, index=df.index, columns = df.columns[col_sep:])
#     return pd.concat([non_features, scaled], axis=1)

if __name__ == "__main__":
    main()