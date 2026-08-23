// [STUDENT-WRITTEN]
import { useState, useEffect, useRef } from 'react'

//logic that finds the users location
//moved from LocationPredictions now the hompage uses it too
export function useGeolocation() {
  const [userLocation, setUserLocation] = useState(null)
  const [locationError, setLocationError] = useState(null)
  const [isLocating, setIsLocating] = useState(false)
  const hasRequestedLocation = useRef(false)

  function requestLocation() {
    setIsLocating(true)
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lon = position.coords.longitude
        setUserLocation({ lat, lon })
        setLocationError(null)
        setIsLocating(false)
      },
      (error) => {
        setLocationError(error)
        setIsLocating(false)
      },
      { timeout: 30000 }
    )
  }

  useEffect(() => {
    if (hasRequestedLocation.current) return
    hasRequestedLocation.current = true
    requestLocation()
  }, [])

  return { userLocation, locationError, isLocating, requestLocation, setUserLocation }
}