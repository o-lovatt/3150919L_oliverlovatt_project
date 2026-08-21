import { useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getLocationsForSpecies } from '../utils/getLocationsForSpecies'
import { useMap } from 'react-leaflet'
import { useEffect } from 'react'
import { getMarkerStyle } from '../utils/markerStyle'
import { MapResizer } from './MapResizer'
import { formatLikelihood } from '../utils/formatLikelihood'
import { getCurrentSeason, getSeason } from '../utils/season'
import { fetchSpeciesRecentSightings } from '../services/api'
import { SPECIES_CODES } from '../utils/speciesCodes'
import { useOnlineStatus } from '../hooks/useOnlineStatus'

const SCOTLAND_CENTER = [56.5, -4.0] //Scotlands centre point (roughly)
const DEFAULT_ZOOM = 6

// map resizer moved into it's own file MapResizer.jsx

// [STUDENT-WRITTEN]
function SpeciesMap({predictions, selectedSpecies, setSelectedSpecies}) {
  //moved to app.jsx for the sidebar

  const isOnline = useOnlineStatus()

  //season selection added for species view
  const [selectedSeason, setSelectedSeason] = useState(getCurrentSeason())
  const SEASONS = ["Spring", "Summer", "Autumn", "Winter"]
  const SEASON_MONTHS = {
    Spring: "March - May",
    Summer: "June - August",
    Autumn: "September - November",
    Winter: "December - February",
  }

  if (!predictions) {
    return <p className="text-charcoal p-4">Loading...</p>
  }

  //get list of unique species names from predictions
  const speciesList = [...new Set(predictions.map(item => item.species))]
  //Set removes duplicated
  //map + [...] turns it into a normal array

  const results = selectedSpecies ? getLocationsForSpecies(predictions, selectedSpecies, selectedSeason) : []

  //... expands the array into individual values
  const maxScore = results.length > 0 ? Math.max(...results.map(item => item.likelihood_score)) : 0

  // formatLikelihood moved int it's own file formatLikelihood.js

  //getMarkerStyle moved into it's own file markerStyle.js


  //fetch live sightings from eBird for species selected
  //the main prediction layer should keep working if this breaks
  //don't show an error, just make the array empty
  const [liveSightings, setLiveSightings] = useState([])
  const [showLiveSightings, setShowLiveSightings] = useState(false)

  useEffect(() => {
    //if !selectedspecies call setLiveSightings
    //look up species code
    //call async fetchSpeciesRecentSightings
    const code = SPECIES_CODES[selectedSpecies]

    if (!selectedSpecies){
      setLiveSightings([])
      return
    }

    async function loadLiveSightings(){
      try {
      const data = await fetchSpeciesRecentSightings(code)
      setLiveSightings(data)
    } catch (err) {
      setLiveSightings([])
    }
  }
  
  loadLiveSightings()

  }, [selectedSpecies])

 
  //create dropdown menu
  return (
    /* [AI-GENERATED - Claude AI 02-08-2026] */
    <div className="h-full flex flex-col">
      <div className="flex flex-wrap gap-1 mb-1">
        <select
          value={selectedSpecies || ""}
          onChange={(e) => setSelectedSpecies(e.target.value)}
          className="px-2 py-2 rounded border border-bark bg-cream text-charcoal text-sm ml-4">
          <option value="">--- Select a species ---</option>
          {speciesList.map(name => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      
        {/* [STUDENT-WRITTEN] */}
          <select
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(e.target.value)}
            className="px-2 py-2 rounded border border-bark bg-cream text-charcoal text-sm">
            {SEASONS.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between ml-4 mr-2">
          <p className="text-charcoal text-xs mb-2 md:mb-0">
            Showing results for {selectedSeason} ({SEASON_MONTHS[selectedSeason]})
          </p>

          {isOnline && (
            <button
              onClick={() => setShowLiveSightings(!showLiveSightings)}
              className="px-3 py-1 rounded text-sm bg-forest text-cream mb-2"
            >
              {showLiveSightings ? "Hide" : "Show"} Live Sightings
            </button>
          )}
          </div>

        {isOnline ? (
        <div className="flex-1 min-h-[300px]">
                <MapContainer center={SCOTLAND_CENTER} zoom={DEFAULT_ZOOM} style={{ height: '100%', width: '100%' }}>
                  <MapResizer />
                  <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                  />

                  {/* [STUDENT-WRITTEN] */}
                  {results.map(item => {
                    const style = getMarkerStyle(item.likelihood_score, maxScore)
                    return(
                      <CircleMarker
                            key={`${item.lat_centre}-${item.lon_centre}`}
                            center={[item.lat_centre, item.lon_centre]}
                            radius={style.radius}
                            pathOptions={{ color: style.color }}
                          >
                            <Popup>
                              <strong>{item.species}</strong>
                              <br />
                              Likelihood: {formatLikelihood(item.likelihood_score)}%
                              <br />
                              Based on: {item.sample_checklists} visits here
                              </Popup>
                          </CircleMarker>
                        )
                      })}

                      {showLiveSightings && liveSightings.map(sighting => {
                        return (
                          <CircleMarker
                            key={sighting.subId}
                            center={[sighting.lat, sighting.lng]}
                            radius={6}
                            pathOptions={{color:"#e53e3e"}}
                          >
                            <Popup>{sighting.locName}
                              <br />
                              {sighting.obsDt}
                            </Popup>
                          </CircleMarker>
                        )
                        })}
                </MapContainer>
              </div>
            ) : (
              <div className="flex-1 min-h-[300px] p-4 overflow-y-auto">
                <p className="text-charcoal font-bold mb-2">You're offline — showing predictions as a list:</p>
                {results.map(item => (
                  <div key={`${item.lat_centre}-${item.lon_centre}`} className="bg-cream border border-bark rounded p-2 mb-2">
                    <p className="text-charcoal text-sm opacity-75">Near {item.lat_centre.toFixed(2)}, {item.lon_centre.toFixed(2)}</p>
                    <p className="text-charcoal">
                      <strong>{item.species}</strong>: {formatLikelihood(item.likelihood_score)}%
                    </p>
                  </div>
                ))}
              </div>
            )}
            </div>
          )
        }
        
        export default SpeciesMap