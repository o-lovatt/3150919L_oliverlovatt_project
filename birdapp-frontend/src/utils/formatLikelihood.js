// [STUDENT WRITTEN]
export function formatLikelihood(score){
const percent = score * 100
if (percent < 1) {
    return percent.toFixed(2) //like 0.33%
} else {
    return Math.round(percent) //like 20%
}
}