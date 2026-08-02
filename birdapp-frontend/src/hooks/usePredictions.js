// [STUDENT-WRITTEN] - skeleton made by [Claude AI 30-07-2026]
import { useState, useEffect } from 'react'
import { fetchVersion, fetchPredictions } from '../services/api'
import { getCachedPredictions, savePredictionsToCache, shouldRefresh } from '../services/cache'


export function usePredictions() {
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadPredictions() {
      // read from cache -> getCachedPredictions
      const cached = await getCachedPredictions();
      if (cached !== null){
        setPredictions(cached)
      }
      // check shouldRefresh()
      const refresh_needed = await shouldRefresh();
  
      //show the predictions?
      //if a refresh is needed call fetchVersion() and fetchPredictions()
      if (refresh_needed === true) {
        const refreshed_ver = await fetchVersion()
        const refreshed_pred = await fetchPredictions()

        await savePredictionsToCache(refreshed_pred, refreshed_ver)
        //update ui
        setPredictions(refreshed_pred)
      }
      //set loading to false at the end
      setLoading(false)
    }

    loadPredictions()
  }, [])

  return { predictions, loading }
}
