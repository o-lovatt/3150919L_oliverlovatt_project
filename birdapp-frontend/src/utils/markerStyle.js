// [STUDENT-WRITTEN]
//gradient colours, pale (low) -> vibrant (high)
//bit hard to decipher on the map? would a dif colour be better?  <--------------------------------------
const LOW_COLOR = {r: 156, g: 156, b: 156 } //pale
const HIGH_COLOR = {r: 15, g: 82, b: 186} //vibrant

export function getMarkerStyle(score, maxScore) {
//how far is score from maxScore
//what if maxScore = 0 ?
const colour_t = score
const radius_t = maxScore > 0 ? score / maxScore : 0


//interpolate each colour channel with t
const red = Math.round(LOW_COLOR.r + colour_t * (HIGH_COLOR.r - LOW_COLOR.r))
const green = Math.round(LOW_COLOR.g + colour_t * (HIGH_COLOR.g - LOW_COLOR.g))
const blue = Math.round(LOW_COLOR.b + colour_t * (HIGH_COLOR.b - LOW_COLOR.b))

//build colour string
const color = `rgb(${red}, ${green}, ${blue})`

//scale radius using t aswell
const minRadius = 4
const maxRadius = 10
const radius = Math.round(minRadius + radius_t * (maxRadius - minRadius))

return {radius: radius, color: color, weight: 2}
}
