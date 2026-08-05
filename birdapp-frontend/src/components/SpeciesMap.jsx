import { useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getLocationsForSpecies } from '../utils/getLocationsForSpecies'
import { useMap } from 'react-leaflet'
import { useEffect } from 'react'
import { getMarkerStyle } from '../utils/markerStyle'
import { MapResizer } from './MapResizer'
import { formatLikelihood } from '../utils/formatLikelihood'

const SCOTLAND_CENTER = [56.5, -4.0] //Scotlands centre point (roughly)
const DEFAULT_ZOOM = 6

// map resizer moved into it's own file MapResizer.jsx

// [STUDENT-WRITTEN]
function SpeciesMap({predictions}) {
  const [selectedSpecies, setSelectedSpecies] = useState(null)

  if (!predictions) {
    return <p className="text-charcoal p-4">Loading...</p>
  }

  //get list of unique species names from predictions
  const speciesList = [...new Set(predictions.map(item => item.species))]
  //Set removes duplicated
  //map + [...] turns it into a normal array

  const results = selectedSpecies ? getLocationsForSpecies(predictions, selectedSpecies) : []

  //... expands the array into individual values
  const maxScore = results.length > 0 ? Math.max(...results.map(item => item.likelihood_score)) : 0

  // formatLikelihood moved int it's own file formatLikelihood.js

  //getMarkerStyle moved into it's own file markerStyle.js
 
  //create dropdown menu
  return (
    /* [AI-GENERATED - Claude AI 02-08-2026] */
    <div>
        <select onChange={(e) => setSelectedSpecies(e.target.value)}
          className="px-4 py-2 rounded border border-bark bg-cream text-charcoal mb-4">
          {speciesList.map(name => (
            <option key={name} value={name}>{name}</option>
            ))}
        </select>
        <div style={{ height: '100vh', width: '100%' }}>
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
                              Based on: {item.sample_checklists} birdwatcher checklists
                              </Popup>
                          </CircleMarker>
                        )
                      })}
                </MapContainer>
              </div>
            </div>
          )
        }
        
        export default SpeciesMap