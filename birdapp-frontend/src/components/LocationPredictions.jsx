import { useState, useEffect } from 'react'
import { usePredictions } from '../hooks/usePredictions'
import { getPredictionsForLocation } from '../utils/getPredictionsForLocation'
import { getLocationsForSpecies } from '../utils/getLocationsForSpecies'

// [STUDENT-WRITTEN] - skeleton provided by Claude AI 30-07-2026
//show the species location based on user location
function LocationPredictions() {
  const { predictions, loading } = usePredictions()
  const [userLocation, setUserLocation] = useState(null)
  const [locationError, setLocationError] = useState(null)

  useEffect(() => {
    //call navigator.geolocation.getCurrentPosition()
    //build {lat, lon} from position.coords.latitude/longitude
    //pass to setLocation()
    navigator.geolocation.getCurrentPosition( //should get GPS without needing data/wifi
      (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude

        const coord_pos = {lat, lon}

        setUserLocation(coord_pos)
      },
      //on error pass error into setLocationError()
      (error) => {
        setLocationError(error)
      }
    )

  }, [])
 
  //work out what predictions to actually show
  const results = (predictions && userLocation) ? getPredictionsForLocation(predictions, userLocation.lat, userLocation.lon) : []

  //show location unavailable message if error 
  //show loading if waiting for location and predictions
  //else show results
   if (locationError) {
        return <p>Location Unavailable: {locationError.message}</p>
    }
    if (!predictions || !userLocation){
      return <p>Loading...</p>
    } 
  return (
    // [AI-GENERATED - Claude AI 31-07-2026]
    <div>
     {results.map(item => (
      <p key={item.species}>{item.species}: {item.likelihood_score}</p>
     ))}
    </div>
  )
}

export default LocationPredictions
