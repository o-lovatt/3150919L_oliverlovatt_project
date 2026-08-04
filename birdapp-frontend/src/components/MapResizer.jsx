import { useMap } from 'react-leaflet'
import { useEffect } from 'react'

//[AI-GENERATED - Claude AI 03-08-2026]
//fix for white space filling most of the UI
export function MapResizer() {
  const map = useMap()

  useEffect(() => {
    map.invalidateSize()
  }, [map])

  return null
}