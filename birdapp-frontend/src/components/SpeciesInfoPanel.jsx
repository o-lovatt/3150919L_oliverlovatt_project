import { useState, useEffect } from 'react'

// [STUDENT-WRITTEN]
//sidebar for showing species info from wikipedia api
//won't work offline
function SpeciesInfoPanel({ speciesName }) {
  const [info, setInfo] = useState(null)
  const [error, setError] = useState(null)

  // [AI-GENERATED - Claude AI 09-08-2026]
  useEffect(() => {
    //if nothing's selected- clear any old info and do nothing else
    if (!speciesName) {
      setInfo(null)
      setError(null)
      return
    }

    // [STUDENT-WRITTEN]
    async function loadInfo() {
     
      //build wiki url
      const title = speciesName.replace(" ", "_")
      const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${title}`
      
      try {
        //fetch url
        const response = await fetch(url);

        //is response ok?
        //if no setError
        //else setInfo
        if (!response.ok){
              setError("Species name doesn't match")
              setInfo(null)
              return

            } else {
              const data = await response.json();
              setInfo(data)
              setError(null)
            }
      } catch (err) {
        setError("Could not load species info")
        setInfo(null)
      }
    }

    loadInfo()
  }, [speciesName])

  if (!speciesName) {
    return null 
  }
  if (error) {
    return <p className="text-bark p-4">{error}</p>
  }
  if (!info) {
    return <p className="text-charcoal p-4">Loading...</p>
  }
  
  return (
    <div className="p-4 h-full overflow-y-auto"> 
      <h2 className="text-charcoal font-bold text-lg">{info.title}</h2>
      {info.thumbnail && (
        <img src = {info.thumbnail.source} alt = {info.title} className="my-2 rounded w-full" /> 
      )}
      <p className="text-charcoal">{info.extract}</p>
    </div>
  )
}

export default SpeciesInfoPanel
