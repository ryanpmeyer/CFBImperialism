# CFBImperialism
An auto-generating implementation of Nathan Bingham's college football imperialism map in Python using folium.
For more information, visit https://www.sbnation.com/college-football/2018/9/4/17816706/college-football-imperialism-map-week-1-2018 .

College football imperialism rules:
  1) All FBS teams begin the season owning the counties which are closest to their stadium (or school in a few cases). This
    distance is defined by the great circle distance between the long/latitudal coordinates of the stadium and the centroid of
    the polygon formed by the county's boundaries.
  2) If a team loses to another team that is represented in my spreadsheet, all of their land will go to the victor.
  3) Ties will cause both teams to keep their respective land areas.
  4) The map is generated on a weekly basis, meaning that all games throughout the week through Saturday will affect that week's
    land changes.

I made this program mostly as a learning tool, but also for personal enjoyment. I will try to add any suggestions given.
