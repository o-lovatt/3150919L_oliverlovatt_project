import { useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { usePredictions } from '../hooks/usePredictions'
import { getLocationsForSpecies } from '../utils/getLocationsForSpecies'
import { useMap } from 'react-leaflet'
import { useEffect } from 'react'

const SCOTLAND_CENTER = [56.5, -4.0] //Scotlands centre point (roughly)
const DEFAULT_ZOOM = 6

//[AI-GENERATED - Claude AI 03-08-2026]
//fix for white space filling most of the UI
function MapResizer() {
  const map = useMap()

  useEffect(() => {
    map.invalidateSize()
  }, [map])

  return null
}

// [STUDENT-WRITTEN]
function SpeciesMap() {
  const { predictions } = usePredictions()
  const [selectedSpecies, setSelectedSpecies] = useState(null)

  if (!predictions) {
    return <p>Loading...</p>
  }

  //get list of unique species names from predictions
  const speciesList = [...new Set(predictions.map(item => item.species))]
  //Set removes duplicated
  //map + [...] turns it into a normal array

  const results = selectedSpecies ? getLocationsForSpecies(predictions, selectedSpecies) : []

  //... expands the array into individual values
  const maxScore = results.length > 0 ? Math.max(...results.map(item => item.likelihood_score)) : 0

  //DON'T LIKE THIS STYLE
  //trying gradient based colour instead
  // function getMarkerStyle(likelihoodScore) {
  //   //may need to update these thresholds based on species data
  //   // vvv
  //   if (likelihoodScore < 0.08) {
  //     return { radius: 6, color: "#a8a8a8" }
  //   } else if (likelihoodScore < 0.15) {
  //     return { radius: 10, color: "#f6ad55" }
  //   } else {
  //     return { radius: 14, color: "#2b6cb0" }
  //   }
  // }

  function formatLikelihood(score){
    const percent = score * 100
    if (percent < 1) {
      return percent.toFixed(2) //like 0.33%
    } else {
      return Math.round(percent) //like 20%
    }
  }

  //gradient colours, pale (low) -> vibrant (high)
  //bit hard to decipher on the map? would a dif colour be better?  <--------------------------------------
  const LOW_COLOR = {r: 219, g: 234, b: 254 } //pale
  const HIGH_COLOR = {r: 30, g: 64, b: 175} //vibrant

  function getMarkerStyle(score, maxScore) {
    //how far is score from maxScore
    //what if maxScore = 0 ?
    const t = maxScore > 0 ? score / maxScore : 0

    //interpolate each colour channel with t
    const red = Math.round(LOW_COLOR.r + t * (HIGH_COLOR.r - LOW_COLOR.r))
    const green = Math.round(LOW_COLOR.g + t * (HIGH_COLOR.g - LOW_COLOR.g))
    const blue = Math.round(LOW_COLOR.b + t * (HIGH_COLOR.b - LOW_COLOR.b))

    //build colour string
    const color = `rgb(${red}, ${green}, ${blue})`

    //scale radius using t aswell
    const minRadius = 5
    const maxRadius = 10
    const radius = Math.round(minRadius + t * (maxRadius - minRadius))
  
    return {radius: radius, color: color}
  }

 
  //create dropdown menu
  return (
    /* [AI-GENERATED - Claude AI 02-08-2026] */
    <div>
        <select onChange={(e) => setSelectedSpecies(e.target.value)}>
          {speciesList.map(name => (
            <option key={name} value={name}>{name}</option>
            ))}
        </select>
        <div style={{ height: '100vh', width: '100%' }}>
                <MapContainer center={SCOTLAND_CENTER} zoom={DEFAULT_ZOOM} style={{ height: '100%', width: '100%' }}>
                  <MapResizer />
                  <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
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
        


      