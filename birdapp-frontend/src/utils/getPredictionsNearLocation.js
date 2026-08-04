import { getCurrentSeason } from "./season"

// [STUDENT-WRITTEN]
import { KM_PER_DEG_LAT, KM_PER_DEG_LON } from "./gridCell"

const RADIUS_KM = 30 //temporarily 30km might change

//use this to calculate distance from users location
export function distanceKm(lat1, lon1, lat2, lon2) {
  //convert the lat difference and lon difference into real km
  const latDiffKm = ((lat2 - lat1) * KM_PER_DEG_LAT)
  const lonDiffKm = ((lon2 - lon1) * KM_PER_DEG_LON)

  // [AI-GENERATED - Claude AI 03-08-2026]
  const distance = Math.sqrt((latDiffKm * latDiffKm) + (lonDiffKm * lonDiffKm))

  return distance;
}

//return predictions within RADIUS km from users location
export function getPredictionsNearLocation(predictions, lat, lon) {
  const season = getCurrentSeason()

  const matching = predictions.filter(item =>
        (item.season === season) &&
        (item.likelihood_score > 0) &&
        distanceKm(lat, lon, item.lat_centre, item.lon_centre) <= RADIUS_KM
    )

    //sort the filtered results by likelihood_score
    matching.sort((a, b) => b.likelihood_score - a.likelihood_score)
    //return the sorted filtered array
    return matching;
}
