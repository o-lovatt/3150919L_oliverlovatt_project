//same maths as build_rpedictions
//GPS coordinate match to same cell

//[STUDENT-WRITTEN]
const CELL_KM = 15;
const REFERENCE_LAT = 56.5;
const KM_PER_DEG_LAT = 111.0;

// [AI-GENERATED - Claude AI 28-07-2026]
const KM_PER_DEG_LON = KM_PER_DEG_LAT * Math.cos(REFERENCE_LAT * Math.PI / 180);

//[STUDENT-WRITTEN]
const LAT_BIN_SIZE = CELL_KM / KM_PER_DEG_LAT;
const LON_BIN_SIZE = CELL_KM / KM_PER_DEG_LON;

//get indicies
export function assignGridCell(lat, lon){
    const lat_idx = Math.floor(lat / LAT_BIN_SIZE)
    const lon_idx = Math.floor(lon / LON_BIN_SIZE)

    return {lat_idx, lon_idx}
}

//get coordinates
export function cellCentre(lat_idx, lon_idx){
    const lat_centre = (lat_idx + 0.5) * LAT_BIN_SIZE;
    const lon_centre = (lon_idx + 0.5) * LON_BIN_SIZE;

    return {lat_centre, lon_centre}
}

export function getGridCellCentre(lat, lon){
    const {lat_idx, lon_idx} = assignGridCell(lat, lon)
    const cell_centre = cellCentre(lat_idx, lon_idx)

    return cell_centre
}
