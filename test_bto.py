from filter_bto import distance_km, find_closest_prediction
import pandas as pd

"""test distance calculation is correct"""
def test_distance_km_known_points():
    #glasgow to edinburgh coordinates
    #should be roughly 65.9km apart
    result = distance_km(55.8617, -4.2583, 55.9533, -3.1883)
    assert abs(result - 65.9) < 1 #(small margin of error allowed)

"""function should return the nearest points score, not the farthest"""
def test_find_closest_prediction_choses_nearest():
    #create fake predictions tabel (only two cells)
    #one near one far
    fake_predictions = pd.DataFrame({
        "lat_centre": [55.86, 0.0], #right next to quesry point
        "lon_centre": [-4.25, 0.0], #far away
        "likelihood_score": [0.5, 0.9],
    })
    #swapping these values makes the test fail as expected
    result = find_closest_prediction(55.87, -4.26, fake_predictions.copy())
    assert result == 0.5
