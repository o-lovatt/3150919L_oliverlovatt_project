import { useState, useEffect, useRef } from 'react'
import { getPredictionsNearLocation } from '../utils/getPredictionsNearLocation'
import { formatLikelihood } from '../utils/formatLikelihood'
import { MapContainer, TileLayer, CircleMarker, Popup, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getMarkerStyle } from '../utils/markerStyle'
import { MapResizer } from './MapResizer'
import { groupPredictionsByLocation } from '../utils/groupPredictionsByLocation'
import L from 'leaflet'
import RecentSightings from './RecentSightings'

// [STUDENT-WRITTEN]
//added functionality for user to click location on map
function LocationClickHandler({ onLocationSelect }) {
  useMapEvents({
    click(e) {
      const clickedLocation = {lat: e.latlng.lat, lon: e.latlng.lng}
      onLocationSelect(clickedLocation)
    },
  })
  return null
}

// [STUDENT-WRITTEN] - skeleton provided by Claude AI 30-07-2026
//show the species location based on user location
function LocationPredictions({predictions, setSelectedSpecies}) {
  const [userLocation, setUserLocation] = useState(null)
  const [locationError, setLocationError] = useState(null)
  const hasRequestedLocation = useRef(false)
  const [showRecentSightings, setShowRecentSightings] = useState(false)

    //(requestLocation now separated from useEffect so it can be called)
    //call navigator.geolocation.getCurrentPosition()
    //build {lat, lon} from position.coords.latitude/longitude
    //pass to setLocation()
    function requestLocation(){
      navigator.geolocation.getCurrentPosition( //should get GPS without needing data/wifi
      (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude

        const coord_pos = {lat, lon}

        setUserLocation(coord_pos)
        setLocationError(null) //clear old error message when someone clicks try again
      },
      //on error pass error into setLocationError()
      (error) => {
        setLocationError(error)
      },
      {timeout: 30000}
    )
  }

  //testing to see if this fixes the 'user denied geolocation prompt' message incorrecly showing
  useEffect(() => {
    if (hasRequestedLocation.current){
      return
    }
    hasRequestedLocation.current = true
    requestLocation()
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
    /* [STUDENT-WRITTEN] */
    <div className="h-full flex flex-col relative">
      <button onClick={() => requestLocation()}
        className="absolute top-4 right-4 z-[1000] px-3 py-2 rounded bg-forest text-cream shadow"
        >
        Recenter
      </button>
        {/* [AI-GENERATED - Claude AI 02-08-2026] */}
        <div className="flex-1">
        <MapContainer center={[userLocation.lat, userLocation.lon]} zoom={9} style={{ height: '100%', width: '100%' }}>
          <LocationClickHandler onLocationSelect={setUserLocation} />
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
              eventHandlers={{click: (e) => {
                L.DomEvent.stopPropagation(e)
              }
            }}
              >
                <Popup>
                  Selected Location
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
                    eventHandlers={{click: (e) => {
                      L.DomEvent.stopPropagation(e)
                    }
                  }}
                >
                  <Popup>
                    {group.species.map(s => (
                      <div key={s.species}>
                        <strong onClick={() =>
                          setSelectedSpecies(s.species)} className="cursor-pointer underline"> {s.species}</strong>: Likelihood {formatLikelihood(s.likelihood_score)}%
                      </div>
                    ))}
                    <div className="mt-2">
                      Based on: {group.species[0].sample_checklists} visits here
                    </div>
                    </Popup>
                </CircleMarker>
              )
            })}
          </MapContainer>
        </div>
        <button
          onClick={() => setShowRecentSightings(!showRecentSightings)}
          className="px-4 py-2 mx-4 mt-2 mb-2 rounded bg-forest text-cream border border-bark"
        >
          {showRecentSightings ? "Hide" : "Show"} Recent Sightings
        </button>
        {showRecentSightings && (
          <RecentSightings lat={userLocation.lat} lon={userLocation.lon} predictions={predictions} />
        )}
      </div>
  )
}

export default LocationPredictions
