// [STUDENT WRITTEN]
export function getLocationsForSpecies(predicitons, speciesName, season){

    const matching = predicitons.filter(item => 
    (item.species === speciesName) && (item.season === season) && (item.likelihood_score > 0)
    )
    //prediction results wers showing cheklists with 0% likelihood_score, added (item.likelihood_score > 0) to fix
    
    // [STUDENT WRITTEN]
    //sort the filtered results by likelihood_score
    matching.sort((a, b) => b.likelihood_score - a.likelihood_score)
    //keep only the top 20
    //updated to fifty to test wether the fronend looks cluttered on common species
    const topResults = matching
    //return the sorted filtered array
    return topResults;
}
