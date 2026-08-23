import { getCurrentSeason } from '../utils/season'
import { formatLikelihood } from '../utils/formatLikelihood'
import { useEffect, useState } from 'react'
import { useGeolocation } from '../hooks/useGeolocation'
import { getPredictionsNearLocation } from '../utils/getPredictionsNearLocation'

// [STUDENT-WRITTEN]
//show top 5 birds 
function HomePage({ predictions, setActiveTab, setSelectedSpecies }) {
    if(!predictions){
        return <p className="text-charcoal p-4"> Loading...</p>
    }

    const {userLocation, locationError} = useGeolocation()
    
    //get current season + predictions filtered by season
    const season = getCurrentSeason()
    
    //display birds based on user location, if can't access location, use top birds from current season
    const sourcePredictions = userLocation
        ? getPredictionsNearLocation(predictions, userLocation.lat, userLocation.lon)
        : predictions.filter(item => item.season === season)

    
    //update score to the highest likelihood
    const bestPerSpecies = {}
    sourcePredictions.forEach(item => {
        if (!bestPerSpecies[item.species] || item.likelihood_score > bestPerSpecies[item.species].likelihood_score){
            bestPerSpecies[item.species] = item
        }
    })

    //creat array, sort be likelihood score
    const topBirds = Object.values(bestPerSpecies).sort((a, b) => b.likelihood_score - a.likelihood_score).slice(0, 5)

    const [images, setImages] = useState({})

    useEffect(() => {
        async function loadImages(){
            for (const bird of topBirds) {

                //build wiki url
                const title = bird.species.replace(" ", "_")
                const url = `https://en.wikipedia.org/api/rest_v1/page/summary/${title}`
                
                    try {
                        //fetch url
                        const response = await fetch(url);

                        //is response ok?
                        if (response.ok){
                            const data = await response.json()
                                if (data.thumbnail) {
                                    setImages(prev => ({ ...prev, [bird.species]: data.thumbnail.source}))
                                }
                            }
                        } catch (err) {
                            //don't do anything here, just skip the image
                        }
                    }
                }
                loadImages()
        }, [userLocation])


    return (
        <div className="p-6 max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold text-charcoal mb-4">Scotland Bird Predictor</h1>
            <p className="text-charcoal mb-6">
                Discover birds that are likely to be seen near you, or search a specific species and see where they are likely to be sighted.
            </p>

            <h2 className="text-xl font-bold text-charcoal mb-2">
                {userLocation ? `Top species near you` : `Top species for ${season}`}</h2>
            <div className="mb-6">
                {topBirds.map(bird => (
                    <div key={bird.species} className="bg-cream border border-bark rounded p-2 mb-2">
                        {images[bird.species] && (
                            <img src={images[bird.species]} alt={bird.species} className="w-16 h-16 object-cover rounded"/>
                        )}
                        <strong 
                            onClick={() => setSelectedSpecies(bird.species)}
                            className="text-charcoal cursor-pointer underline"
                            >
                                {bird.species}
                            </strong>
                        <span className="text-charcoal"> - {formatLikelihood(bird.likelihood_score)}% Likelihood</span>
                    </div>
                ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
                <button
                    onClick={() => setActiveTab("location")}
                    className="flex-1 px-4 py-3 rounded bg-forest text-cream font-semibold">
                        Find Birds Near Me
                </button>
                <button
                    onClick={() => setActiveTab("species")}
                    className="flex-1 px-4 py-3 rounded bg-forest text-cream font-semibold">
                        Search By Species
                </button>
            </div>
        </div>
    )
}
export default HomePage
