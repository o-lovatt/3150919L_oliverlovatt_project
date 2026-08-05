import { useState, useEffect } from 'react'
import { getPredictionsNearLocation } from '../utils/getPredictionsNearLocation'
import { formatLikelihood } from '../utils/formatLikelihood'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getMarkerStyle } from '../utils/markerStyle'
import { MapResizer } from './MapResizer'
import { groupPredictionsByLocation } from '../utils/groupPredictionsByLocation'

// [STUDENT-WRITTEN] - skeleton provided by Claude AI 30-07-2026
//show the species location based on user location
function LocationPredictions({predictions}) {
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
 

  //show location unavailable message if error 
  //show loading if waiting for location and predictions
  //else show results
   if (locationError) {
        return <p className="text-bark p-4">Location Unavailable: {locationError.message}</p>
    }
    if (!predictions || !userLocation){
      return <p className="text-charcoal p-4">Loading...</p>
    } 
  
  //same as SpeciesMap
  const results = getPredictionsNearLocation(predictions, userLocation.lat, userLocation.lon)

  const grouped = groupPredictionsByLocation(results)

  const maxScore = results.length > 0 ? Math.max(...results.map(item => item.likelihood_score)) : 0
  
  return (
    /* [AI-GENERATED - Claude AI 02-08-2026] */
    <div>
      <div style={{ height: '100vh', width: '100%' }}>
        <MapContainer center={[userLocation.lat, userLocation.lon]} zoom={9} style={{ height: '100%', width: '100%' }}>
          <MapResizer />
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {/* [STUDENT-WRITTEN] */}
          <CircleMarker
            center={[userLocation.lat, userLocation.lon]}
            radius={6}
            pathOptions={{ color: "red" }}
            >
              <Popup>
                Your Location
                </Popup>
            </CircleMarker>

            {grouped.map(group => {
              const bestScore = Math.max(...group.species.map(s => s.likelihood_score))
              const style = getMarkerStyle(bestScore, maxScore)
              return(
                <CircleMarker
                      key={`${group.lat_centre}-${group.lon_centre}`}
                      center={[group.lat_centre, group.lon_centre]}
                      radius={style.radius}
                      pathOptions={{color: style.color}}
                    >
                      <Popup>
                        {group.species.map(s => (
                          <div key={s.species}>
                            <strong>{s.species}</strong>: seen on {formatLikelihood(s.likelihood_score)}% of {s.sample_checklists} visits here
                          </div>
                        ))}
                        </Popup>
                    </CircleMarker>
                  )
                })}
        </MapContainer>
      </div>
    </div>
  )
}

export default LocationPredictions
