import { getCurrentSeason } from "./season"

// [STUDENT WRITTEN]
export function getLocationsForSpecies(predicitons, speciesName){
    const season = getCurrentSeason()

    const matching = predicitons.filter(item => 
    (item.species === speciesName) && (item.season === season) && (item.likelihood_score > 0)
    )
    //prediction results wers showing cheklists with 0% likelihood_score, added (item.likelihood_score > 0) to fix
    
    // [STUDENT WRITTEN]
    //sort the filtered results by likelihood_score
    matching.sort((a, b) => b.likelihood_score - a.likelihood_score)
    //keep only the top 20
    const topResults = matching.slice(0, 20)
    //return the sorted filtered array
    return topResults;
}
