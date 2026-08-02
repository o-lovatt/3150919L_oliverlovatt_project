// [STUDENT-WRITTEN]
import { openDB } from 'idb';

const DB_NAME = 'birdapp-cache';
const DB_VERSION = 1;
const STORE_NAME = 'predictions';
const REFRESH_INTERVAL_MS = 24 * 60 * 60 * 1000; //24 hours

async function getDB(){
    return openDB(DB_NAME, DB_VERSION, {
        upgrade(db) {
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME)
            }
        },
    });
}

//save predictions in array
export async function savePredictionsToCache(predictions, versionInfo) {
    const db = await getDB()
    await db.put(STORE_NAME, predictions, "predictions")
    await db.put(STORE_NAME, versionInfo, "version")
    await db.put(STORE_NAME, Date.now(), "lastChecked")
}

//read cached predictions
//return null if nothing is cached
export async function getCachedPredictions(){
    const db = await getDB()
    const value = await db.get(STORE_NAME, "predictions")

    if (value === undefined) {
        return null
    } else {
        return value
    }
}

//read cached version
export async function getCachedVersion(){
    const db = await getDB()
    const version = await db.get(STORE_NAME, "version")

    if(version === undefined){
        return null
    } else {
        return version
    }
}


//see if it's time for a refresh
export async function shouldRefresh(){
    const db = await getDB()
    const lastChecked = await db.get(STORE_NAME, "lastChecked")

    if (lastChecked === undefined){
        return true
    }

    const timeSinceLastCache = Date.now() - lastChecked

    // [STUDENT-WRITTEN]
    if (timeSinceLastCache > REFRESH_INTERVAL_MS){
        return true
    } else {
        return false
    }
}