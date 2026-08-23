import { useState } from 'react'
import './App.css'
import { usePredictions } from './hooks/usePredictions'
import LocationPredictions from './components/LocationPredictions'
import SpeciesMap from './components/SpeciesMap'
import SpeciesInfoPanel from './components/SpeciesInfoPanel'
import HomePage from './components/HomePage'

// [STUDENT-WRITTEN]
function App() {
  //refactored, now only called once
  const { predictions, loading } = usePredictions()

  //track which view is active
  const [activeTab, setActiveTab] = useState("home")

  //for sidebar
  const [selectedSpecies, setSelectedSpecies] = useState(null)

  //navigation tabs
  return (
    <div className="h-dvh bg-cream flex flex-col md:flex-row overflow-y-auto">
      <div className="flex-1 flex flex-col">
        {activeTab !== "home" && (
        <div className="flex gap-1 px-4 pt-4 pb-2">
          <button onClick={() => setActiveTab("home")}
          className={`px-4 py-2 rounded ${activeTab ==="home" ? "bg-forest text-cream" : "bg-cream text-charcoal border border-bark"}`}
          aria-label = "Go to Homepage"
          >
            Home
          </button>

          <button onClick={() => {
            setActiveTab("location")
            setSelectedSpecies(null)
          }}
          className={`px-4 py-2 rounded ${activeTab ==="location" ? "bg-forest text-cream" : "bg-cream text-charcoal border border-bark"}`}
          aria-label = "Find nearby birds in your location"
          >
            Location
          </button>

          <button onClick={() => setActiveTab("species")}
          className={`px-4 py-2 rounded ${activeTab ==="species" ? "bg-forest text-cream" : "bg-cream text-charcoal border border-bark"}`}
          aria-label = "Find sighting locations based on a specific species"
          >
            Species
          </button>
        </div>
        )}

        <div className="flex-1">
          {activeTab === "home" ? (
            <HomePage predictions={predictions} setActiveTab={setActiveTab} setSelectedSpecies={setSelectedSpecies}/>
          ) : activeTab === "location" ? (
            <LocationPredictions predictions = {predictions} setSelectedSpecies = {setSelectedSpecies}/>
          ) : (
          <SpeciesMap
            predictions={predictions}
            selectedSpecies={selectedSpecies}
            setSelectedSpecies={setSelectedSpecies}
            />
          )}
        </div>
      </div>

      {/* only render sidebar when selecteSpecies has a value*/}
        {selectedSpecies && (
          <div className="w-full md:w-80 bg-cream">
            <SpeciesInfoPanel speciesName={selectedSpecies}/>
          </div>
        )}
      </div>
    )
  }

//removed old test blocks

export default App
