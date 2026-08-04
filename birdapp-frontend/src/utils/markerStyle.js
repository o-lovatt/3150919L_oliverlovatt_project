// [STUDENT-WRITTEN]
//gradient colours, pale (low) -> vibrant (high)
//bit hard to decipher on the map? would a dif colour be better?  <--------------------------------------
const LOW_COLOR = {r: 219, g: 234, b: 254 } //pale
const HIGH_COLOR = {r: 30, g: 64, b: 175} //vibrant

export function getMarkerStyle(score, maxScore) {
//how far is score from maxScore
//what if maxScore = 0 ?
const t = maxScore > 0 ? score / maxScore : 0

//interpolate each colour channel with t
const red = Math.round(LOW_COLOR.r + t * (HIGH_COLOR.r - LOW_COLOR.r))
const green = Math.round(LOW_COLOR.g + t * (HIGH_COLOR.g - LOW_COLOR.g))
const blue = Math.round(LOW_COLOR.b + t * (HIGH_COLOR.b - LOW_COLOR.b))

//build colour string
const color = `rgb(${red}, ${green}, ${blue})`

//scale radius using t aswell
const minRadius = 5
const maxRadius = 10
const radius = Math.round(minRadius + t * (maxRadius - minRadius))

return {radius: radius, color: color}
}
