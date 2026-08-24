import { useState, useEffect, useRef } from 'react'
import { getPredictionsNearLocation } from '../utils/getPredictionsNearLocation'
import { formatLikelihood } from '../utils/formatLikelihood'
import { MapContainer, TileLayer, CircleMarker, Popup, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getMarkerStyle } from '../utils/markerStyle'
import { MapResizer } from './MapResizer'
import { groupPredictionsByLocation } from '../utils/groupPredictionsByLocation'
import L from 'leaflet'
import { useOnlineStatus } from '../hooks/useOnlineStatus'
import { useGeolocation } from '../hooks/useGeolocation'
import { useRecentSightings } from '../hooks/useRecentSightings'
import { groupSightingsByLocation } from '../utils/groupSightingsByLocation'

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
  const [showRecentSightings, setShowRecentSightings] = useState(false)
  const isOnline = useOnlineStatus()

  //requestLocation now moved to useGeolocation
  const { userLocation, locationError, isLocating, requestLocation, setUserLocation } = useGeolocation()

  //useRecentSightings needs userLocation
  //what if user location is null?
  //get hook to handle undefined lat/lon vars
  const { sightings: recentSightings, error: recentSightingsError } = useRecentSightings(
    userLocation?.lat,
    userLocation?.lon,
    predictions
  )

  //guard if recentSightings is null
  const groupedSightings = recentSightings ? groupSightingsByLocation(recentSightings) : []

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
        className="absolute top-12 right-4 z-[1000] px-3 py-2 rounded bg-forest text-cream shadow"
        >
        {isLocating ? "Locating..." : "Recenter"}
      </button>

      <div className="flex flex-col md:flex-row md:justify-end mx-4 mb-2">
        {isOnline && (
          <button
            onClick={() => setShowRecentSightings(!showRecentSightings)}
            className="w-full md:w-auto px-3 py-1 text-sm rounded bg-forest text-cream"
          >
            {showRecentSightings ? "Hide" : "Show"} Live Sightings
          </button>
        )}
      </div>

      {isOnline ? (
        <div className="flex-1 min-h-[300px]">
        {/* [AI-GENERATED - Claude AI 02-08-2026] */}
        <MapContainer center={[userLocation.lat, userLocation.lon]} zoom={9} style={{ height: '100%', width: '100%' }}>
          <LocationClickHandler onLocationSelect={setUserLocation} />
            <MapResizer />
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            />

            {/* [STUDENT-WRITTEN] */}
            <CircleMarker
              //user location marker
              center={[userLocation.lat, userLocation.lon]}
              radius={6}
              pathOptions={{ color: "green" }}
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
              
            {showRecentSightings && groupedSightings.map(group => (
              //new block to show recent sightings as circle markers (same as species view)
                <CircleMarker
                  key={`${group.lat}-${group.lng}`}
                  center={[group.lat, group.lng]}
                  radius={6}
                  pathOptions={{ color: "#e53e3e" }}
                >
                  <Popup>
                    {group.sightings.map(s => (
                      //edited to group sightings from the same checklist into one circle marker
                      <div key={s.subId}>
                        <strong
                          onClick={() => setSelectedSpecies(s.comName)}
                          className='cursor-pointer underline'
                          >
                          {/* comName is optional, added diplay for when missing this value*/}
                          {s.comName}
                        </strong>
                        : {s.howMany ? `${s.howMany} seen` : "seen"}
                      </div>
                    ))}
                    <div className="mt-2 text-xs opacity-75">
                      {group.locName}
                      <br />
                      {group.sightings[0].obsDt}
                    </div>
                  </Popup>
                </CircleMarker>
              ))}

          </MapContainer>
        </div>
      ) : (
        <div className="flex-1 min-h-[300px] p-4 overflow-y-auto">
          <p className="text-charcoal font-bold mb-2">You're Offline - showing predictions as a list:</p>
           {grouped.map(group => (
            <div key={`${group.lat_centre}-${group.lon_centre}`} className="bg-cream border border-bark rounded p-2 mb-2">
              <p className="text-charcoal text-sm opacity-75">Near {group.lat_centre.toFixed(2)}, {group.lon_centre.toFixed(2)}</p>
              {group.species.map(s => (
                <p key={s.species} className="text-charcoal">
                  <strong>{s.species}</strong>: {formatLikelihood(s.likelihood_score)}%
                </p>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default LocationPredictions
