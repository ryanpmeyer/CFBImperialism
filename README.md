# CFBImperialism
An auto-generating implementation of Nathan Bingham's college football imperialism map in Python with Folium.
For more information, visit https://www.sbnation.com/college-football/2018/9/4/17816706/college-football-imperialism-map-week-1-2018 .

![img](https://raw.githubusercontent.com/ryanpmeyer/CFBImperialism/master/preseason_map_preview.PNG)


College football imperialism rules:
  1) All FBS teams begin the season owning the counties which are closest to their stadium (or school in a few cases). This distance is defined by the great circle distance between the long/latitudal coordinates of the stadium and the centroid of the polygon formed by the county's boundaries.
  2) If a team loses to another team that is represented in my spreadsheet, all of their land will go to the victor.
  3) Ties will cause both teams to keep their respective land areas.
  4) The map is generated on a weekly basis, meaning that all games throughout the week through Saturday will affect that week's land changes.
    
Some implementation details:
  The program draws a geojson overlay on top of the United States, where the color style parameters are determined by the owning team's primary color. This was done by finding a US county geojson file and adding extra data to each county representing the team name and hex value of the color, and exporting this information into a new geojson file with pandas. To get game results, the program scrapes data from the HTML of NCAA.com's football scores page. Out of respect for their site's servers, I have and will continue to simply save a copy of the html from my browser and scraping the scores from that each week, since these sports websites tend to frown upon bots/scripts requesting data from them all the time. In drawing the logos over the areas on the map, the program uses the k-means algorithm to identify clustered counties and find the approximate center of each cluster. This is not perfect, as currently there is no good way to automatically know how many clusters should be identified. As of right now, the program overcomes this by giving each school a starting k value (the Washington Huskies for example can't have a starting k = 1 because it owns most of the state of Washington and Alaska, and it would appear more natural to have a logo over each of those land masses), and transferring that k value along with the land when a school loses a game.

  I made this program mostly as a learning tool, but also for personal enjoyment. I will try to add any suggestions given. Currently, it is pretty slow, especially in generating the preseason map, because a lot of numbers need to be crunched to find the centroids of each county and their distance to each school. I plan to parallelize this in the future to improve the time spent generating datasets and maps. Originally, I had every step of the process in a separate Python script, but have moved everything into one file so it is all as automated as possible. As a result, the program computes all of the weeks' maps at once, rather than saving each week and using the previous week's files to generate the next week. This was to allow the ease of changing parameters in my handmade school spreadsheet such as logo images and colors, and regenerating all of the maps at once.
