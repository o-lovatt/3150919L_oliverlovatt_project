import { getGridCellCentre } from "./gridCell"
import { getCurrentSeason } from "./season"


// [STUDENT WRITTEN]
export function getPredictionsForLocation(predicitons, lat, lon){
    const cell = getGridCellCentre(lat, lon)
    const season = getCurrentSeason()
    
    // [Claude AI 30-07-2026]
    // filter 'prediction` down to rows where lat_centre/lon_centre match `cell` AND season matches `season`
    const matching = predicitons.filter(item =>
        Math.abs(item.lat_centre - cell.lat_centre) < 0.0001 &&
        Math.abs(item.lon_centre - cell.lon_centre) < 0.0001 &&
        item.season === season 
    )
    // [STUDENT WRITTEN]
    //sort the filtered results by likelihood_score
    matching.sort((a, b) => b.likelihood_score - a.likelihood_score)
    //return the sorted filtered array
    return matching;
}

