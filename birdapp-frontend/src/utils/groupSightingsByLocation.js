// [STUDENT-WRITTEN]
//group live sightings based on location for 'location' view live sighting markers
//similar to groupPredictionByLocation
export function groupSightingsByLocation(sightings) {
  const groups = {}

  sightings.forEach(sighting => {
    const key = `${sighting.lat}-${sighting.lng}`

    //if groups[key] doesn't exist create it
    if (!groups[key]){
        groups[key] = {lat: sighting.lat, lng: sighting.lng, locName: sighting.locName, sightings: []}
    }

    //push sightings info into groups sightings array
    groups[key].sightings.push({comName: sighting.comName, howMany: sighting.howMany, obsDt: sighting.obsDt, subId: sighting.subId})
  })
  //convert groups to array and return
  const allGroups = Object.values(groups)
  return allGroups
}