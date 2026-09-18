// Embed the handwritten strokes as a PNG so browser printing does not depend
// on inline SVG painting or external image requests.
export function signatureImage(strokes) {
  if (!Array.isArray(strokes) || !strokes.length) return ''
  const canvas = document.createElement('canvas')
  canvas.width = 1200
  canvas.height = 480
  const context = canvas.getContext('2d')
  if (!context) throw new Error('서명 이미지를 준비하지 못했습니다.')
  context.fillStyle = '#ffffff'
  context.fillRect(0, 0, canvas.width, canvas.height)
  context.strokeStyle = '#101114'
  context.lineWidth = 10
  context.lineCap = 'round'
  context.lineJoin = 'round'
  for (const stroke of strokes) {
    if (!stroke.length) continue
    context.beginPath()
    context.moveTo(stroke[0][0] * canvas.width, stroke[0][1] * canvas.height)
    for (const [x, y] of stroke.slice(1)) context.lineTo(x * canvas.width, y * canvas.height)
    context.stroke()
  }
  return canvas.toDataURL('image/png')
}
