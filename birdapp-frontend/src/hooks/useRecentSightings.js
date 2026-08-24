import { useState, useEffect } from 'react'
import { fetchRecentSightings } from '../services/api'

export function useRecentSightings(lat, lon, predictions) {
  const [sightings, setSightings] = useState(null)
  const [error, setError] = useState(null)

  const speciesList = [...new Set(predictions.map(item => item.species))]

  useEffect(() => {
    if (!lat || !lon){
        return // don't attempt if userLocation is undefined
    }
    async function loadSightings() {
        //call fetchrecentSighings
        //setSightings with result
        //else error
        try {
            const data = await fetchRecentSightings(lat, lon)
            setSightings(data)
        } catch (err) {
            setError("could not load recent sightings")
        }
    }
    loadSightings()
  }, [lat, lon])

  //filter to shortlist species once sightings have loaded or stay null
  const filteredSightings = sightings
    ? sightings.filter(sighting => speciesList.includes(sighting.comName))
    : null

  return { sightings: filteredSightings, error }
}