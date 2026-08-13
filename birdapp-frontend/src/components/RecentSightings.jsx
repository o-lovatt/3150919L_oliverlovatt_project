// [STUDENT-WRITTEN - skeleton provided by Claude 13-08-2026]
import { useState, useEffect } from 'react'
import { fetchRecentSightings } from '../services/api'


//shows live eBird sightings in the last 7 days
function RecentSightings({lat, lon, predictions}) {
  const [sightings, setSightings] = useState(null)
  const [error, setError] = useState(null)

  const speciesList = [...new Set(predictions.map(item => item.species))]
  
  useEffect(() => {
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

  if (error) {
    return (
      <div className="p-4 text-bark text-sm">
        Recent sightings unavailable right now.
      </div>
    )
  }

  if (!sightings) {
    return (
      <div className="p-4 text-charcoal text-sm">
        Loading recent sightings...
      </div>
    )
  }

  const filteredSightings = sightings.filter(sighting => speciesList.includes(sighting.comName)) //[AI-GENERATED - Claude AI 13-08-2026]
  console.log("speciesList:", speciesList)
  console.log("raw sighting names:", sightings.map(s => s.comName))
  console.log("filtered count:", filteredSightings.length, "of", sightings.length, "total")

  if (filteredSightings.length === 0) {
    return (
      <div className="p-4 text-charcoal text-sm">
        No recent sightings reported nearby in the last 7 days.
      </div>
    )
  }

  //[AI-GENERATED - Claude AI 13-08-2026]
  return (
    <div className="p-4">
      <h3 className="text-charcoal font-bold mb-2">Recent Sightings Nearby</h3>
      <div className="max-h-64 overflow-y-auto space-y-2">
        {filteredSightings.slice(0, 20).map((sighting, index) => (
          <div key={`${sighting.subId}-${sighting.speciesCode}-${index}`} className="bg-cream border border-bark rounded p-2">
            <p className="text-charcoal font-semibold">{sighting.comName}</p>
            <p className="text-charcoal text-sm">
              {sighting.howMany} seen at {sighting.locName}
            </p>
            <p className="text-charcoal text-xs opacity-75">{sighting.obsDt}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RecentSightings
