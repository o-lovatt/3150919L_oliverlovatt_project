//predicted sightings based on the users location were overlapping on the frontend
//think a better way to display this is a list instead of the location circles

// [STUDENT-WRITTEN]
export function groupPredictionsByLocation(results) {
  const groups = {}

  results.forEach(item => {
    const key = `${item.lat_centre}-${item.lon_centre}`

    if (!groups[key]){
      groups[key] = {lat_centre: item.lat_centre, lon_centre: item.lon_centre, species: []}
    }

    groups[key].species.push({species: item.species, likelihood_score: item.likelihood_score, sample_checklists: item.sample_checklists})
  })
  //limit popup to only show top 5 most likely species in area, added after species list was increased
  const allGroups = Object.values(groups)
  allGroups.forEach(group => {
    group.species.sort((a, b) => b.likelihood_score - a.likelihood_score)
    group.species = group.species.slice(0, 5)
  })
return allGroups
}
