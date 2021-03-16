export default function loaderAnimation($circle, totalTime, totalDist) {
  const start = Date.now()

  const tick = () => {
    const now = Date.now()
    let diff = (now - start) / totalTime

    $circle.setAttribute("stroke-dasharray", (Math.min(diff, 1) * totalDist) + ", 20000")
    if (diff <= 1) {
      requestAnimationFrame(tick)
    }
  }
  tick()
}
