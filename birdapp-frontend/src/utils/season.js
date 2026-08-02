//get date objects and figure out what month it is
//[STUDENT-WRITTEN]

export function getSeason(date){
    const month = date.getMonth(); //0-11#
    const MONTH_TO_SEASON = {
        11: "Winter", 0: "Winter", 1: "Winter",
        2: "Spring", 3: "Spring", 4: "Spring",
        5: "Summer", 6: "Summer", 7: "Summer",
        8: "Autumn", 9: "Autumn", 10: "Autumn",
    };
    return MONTH_TO_SEASON[month];
}

export function getCurrentSeason(){
    return getSeason(new Date());
}