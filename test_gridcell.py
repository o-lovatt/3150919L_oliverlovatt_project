from build_predictions import assign_grid_cell, cell_centre
from constants import LAT_BIN_SIZE

"""test grid cell returns real numbers, not NaN"""
def test_assign_grid_cell_basic():
    #know coordinate should map to a cell
    lat_idx, lon_idx = assign_grid_cell(56.5, -4.0)
    #check it returns numbers and not None/NaN
    assert lat_idx is not None
    assert lon_idx is not None

"""assing cell, convert back to centre point, result should be similar to original coordinate"""
def test_cell_centre_conversion():
    #assign cell
    #convert to centre point
    #should be identical/very close to original coordinate
    lat_idx, lon_idx = assign_grid_cell(56.5, -4.0)
    lat_centre, lon_centre = cell_centre(lat_idx, lon_idx)
    #close a.k.a within one cell width
    assert abs(lat_centre - 56.5) < 0.5 
    assert abs(lon_centre - (-4.0)) < 0.5

"""test if two close coordinates get differnt lat_idx/lon_idx values if theye are in different bins"""
def test_nearby_points_can_land_in_different_cells():
    lat_idx_1, lon_idx_1 = assign_grid_cell(56.5, -4.0)
    lat_idx_2, lon_idx_2 = assign_grid_cell(56.500 + LAT_BIN_SIZE + 0.001, -4.0) #0.001 ensures point is definitely past grid cell boundary
    assert lat_idx_1 != lat_idx_2

"""opposite case of test above, points in the same bin should share a grid cell"""
def test_nearby_points_land_in_same_cell():
    lat_idx_1, lon_idx_1 = assign_grid_cell(56.500, -4.0)
    lat_idx_2, lon_idx_2 = assign_grid_cell(56.500 + (LAT_BIN_SIZE/4), -4.0)
    assert lat_idx_1 == lat_idx_2