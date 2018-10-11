from math import radians, sin, cos, sqrt, atan
from scipy.cluster.vq import kmeans
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import folium
import json

curr_week = 7

def generate_json(week):
    if (week == "_pre"):
        generate_starting_counties()
        return
    elif (week == 0):
        input_filename = "week_pre.json"
    else:
        input_filename = "week{}.json".format(week - 1)
    counties = pd.read_json(input_filename)['features']
    json_out = {"type" : "FeatureCollection", "features" : []}
    results = {} #loser : winner

    ###Get scores from html
    html = open("week{}.html".format(week))
    soup = BeautifulSoup(html, "html.parser")
    teams = map(
        lambda x : x.get_text(),
        soup.find_all("span", class_="gamePod-game-team-name")
    )
    scores = map(
        lambda x : x.get_text(),
        soup.find_all("span", class_="gamePod-game-team-score")
    )
    games = list(zip(teams, scores))

    ###Subroutine for getting DataFrame index of school given name
    def find_school(name):
        index = -1
        for j in range(len(schools.values)):
            if schools['School'][j] == name:
                index = j
                break
        if index == -1:
            print("school not found: {:>20}".format(name))
        return index

    ###Populate game results
    for i in range(0, len(games) - 1, 2):
        team_1, score_1 = games[i]
        team_2, score_2 = games[i+1]
        score_1, score_2 = int(score_1), int(score_2)
        if (score_1 < score_2):
            results[team_1] = team_2
        elif (score_2 < score_1):
            results[team_2] = team_1

    ###Update K values for K means
    for loser in results.keys():
        winner = results[loser]
        w_index = find_school(winner)
        l_index = find_school(loser)
        if (w_index != -1 and l_index != -1):
            schools['K'][w_index] += schools['K'][l_index]
            schools['K'][l_index] = 0
            school_centroids[w_index].extend(school_centroids[l_index])
            school_centroids[l_index] = []

    ###Recolor and relabel counties based on winners/losers
    for i in range(len(counties)):
        school = counties[i]['school']
        json_out['features'].append(counties[i])
        if school in results.keys(): #if school is a loser
            index = find_school(results[school])
            if (index != -1):
                json_out['features'][i]['school'] = results[school]
                json_out['features'][i]['color'] = schools['Color'][index]

    output_file = open("week{}.json".format(week), "w")
    output_file.write(json.dumps(json_out))
    output_file.close()

def generate_map(week, logos_enabled = True, schools_enabled = False):
    CENTER = (39.8283, -98.5795)
    DEFAULT_ZOOM = 4
    geojson_filename = "week{}.json".format(week)

    map = folium.Map(
        location = CENTER,
        tiles = 'CartoDB positron',
        zoom_start = DEFAULT_ZOOM
    )

    def style(feature):
        return {
            'fillOpacity'   : .85,
            'fillColor'     : feature['color'],
            'weight'        : 0.75,
            'color'         : 'black'
        }

    def draw_counties(geojson_filename):
        folium.GeoJson(
            data = geojson_filename,
            name = 'geojson',
            style_function = style
        ).add_to(map)

    def draw_schools():
        for i in range(len(schools.values)):
            popup = folium.Popup(schools['School'][i], parse_html = True)
            location = [schools['Lat'][i], schools['Long'][i]]
            folium.Marker(location, popup = popup).add_to(map)

    def draw_logos():
        clusters = find_clusters()
        for i in range(len(clusters)):
            location = [clusters['Lat'][i], clusters['Long'][i]]
            icon = folium.features.CustomIcon(
                icon_image = clusters['Logo'][i],
                icon_size = (35, 35),
                icon_anchor = None
            )
            folium.Marker(
                location = location,
                tooltip = clusters['School'][i],
                icon = icon
            ).add_to(map)

    def find_clusters():
        school_clusters = []
        school_names = []
        logos = []
        for i in range(len(school_centroids)):
            k = schools['K'][i]
            if k != 0:
                cluster, _ = kmeans(school_centroids[i], k)
                for j in range(len(cluster)):
                    school_clusters.append(cluster[j])
                    school_names.append(schools['School'][i])
                    logos.append(schools['Logo'][i])
        school_clusters = np.array(school_clusters)
        return pd.DataFrame({
            "Lat"       : school_clusters[:,0],
            "Long"      : school_clusters[:,1],
            "School"    : school_names,
            "Logo"      : logos
        })

    draw_counties('week{}.json'.format(week))
    folium.LayerControl().add_to(map)
    if(logos_enabled):
        draw_logos()
    if(schools_enabled):
        draw_schools()
    map.save('map_week{}.html'.format(week))


def generate_starting_counties():
    county_data = pd.read_json('counties_lowres.json', precise_float = True)['features']
    def polygon_center(vertices):
        if(len(vertices) < 2):
            vertices = vertices[0]
        area_total = 0
        centroid_total = [float(vertices[0][0]), float(vertices[0][1])]
        for i in range(0, len(vertices) - 2):
            a, b, c = vertices[0], vertices[i+1], vertices[i+2]
            area = ((a[0] * (b[1] - c[1])) +
                    (b[0] * (c[1] - a[1])) +
                    (c[0] * (a[1] - b[1]))) / 2.0;
            if area == 0:
                continue
            centroid = [(a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0]
            centroid_total[0] = ((area_total * centroid_total[0]) +
                                 (area * centroid[0])) / (area_total + area)
            centroid_total[1] = ((area_total * centroid_total[1]) +
                                 (area * centroid[1])) / (area_total + area)
            area_total += area
        return [centroid_total[1], centroid_total[0]]

    def haversine_distance(a, b):
        radius = 6371
        phi_1 = radians(a[0])
        phi_2 = radians(b[0])
        delta_phi = radians(b[0] - a[0])
        delta_lambda = radians(b[1] - a[1])
        a = (sin(delta_phi / 2.0) ** 2 + cos(phi_1)
            * cos(phi_2) * sin(delta_lambda / 2.0) ** 2)
        c = 2 * atan(sqrt(a) / sqrt(1-a))
        d = radius * c
        return d

    def find_closest_schools():
        county_matrix = [[] for _ in range(len(schools.values))]
        for i in range(len(county_data.values)):
            vertices = county_data[i]['geometry']['coordinates'][0]
            centroid = polygon_center(vertices)
            min_dist = float('inf')
            school_index = None
            for j in range(len(schools.values)):
                location = [schools['Lat'][j], schools['Long'][j]]
                dist = haversine_distance(centroid, location)
                if dist < min_dist:
                    min_dist = dist
                    school_index = j
            county_matrix[school_index].append(i)
            school_centroids[school_index].append(centroid)
        return county_matrix

    new_geojson = {"type" : "FeatureCollection", "features" : []}
    county_matrix = find_closest_schools()

    for i in range(len(county_matrix)):
        for j in county_matrix[i]:
            county = county_data[j]
            county['color'] = schools['Color'][i]
            county['school'] = schools['School'][i]
            new_geojson["features"].append(county)

    output_file2 = open("week_pre.json", "w")
    output_file2.write(json.dumps(new_geojson))
    output_file2.close()

schools = pd.read_csv('SchoolData.csv')
school_centroids = [[] for _ in range(len(schools.values))]
generate_json("_pre")
generate_map("_pre")
for i in range(curr_week):
    generate_json(i)
    generate_map(i)
