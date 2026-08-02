import { useState } from 'react'
import reactLogo from './assets/react.svg' //will need these later
import viteLogo from './assets/vite.svg' //will need these later
import heroImg from './assets/hero.png' //might need this later??
import './App.css'
import { useEffect } from 'react';
import { usePredictions } from './hooks/usePredictions'
import { getPredictionsForLocation } from './utils/getPredictionsForLocation'
import LocationPredictions from './components/LocationPredictions'

// [STUDENT-WRITTEN]
//test userLocation + prediction

function App() {
  return (
    <div>
      <LocationPredictions />
    </div>
  )
}


// // [STUDENT-WRITTEN]
// //test cached 
// function App() {
//   const { predictions, loading } = usePredictions()
//   return (
//     <div>
//       {predictions ? <p>{JSON.stringify(predictions)}</p> : <p>Nothing cached yet</p>}
//     </div>
//   )
// }

// // [STUDENT-WRITTEN]
// //test api.js and cache.js

// function App() {
//   const [version, setVersion] = useState(null)

//   useEffect(() => {
//     async function returnVersion() {
//       const data = await fetchPredictions();
//       setVersion(data);
//     }
//     returnVersion()
//   }, []);

//   useEffect(() => {
//     async function testCache() {
//           const before = await shouldRefresh();
//           console.log("should refresh (before caching anything):", before);

//           await savePredictionsToCache(["test"], { generated_at: new Date().toISOString(), row_count: 1 });

//           const after = await shouldRefresh();
//           console.log("should refresh (right after caching):", after);
//       }
//       testCache()
//   }, []);

//   return (
//     <div>
//       {version ? <p>{JSON.stringify(version)}</p> : <p>Loading...</p>}
//     </div>
//   )
// }

export default App
