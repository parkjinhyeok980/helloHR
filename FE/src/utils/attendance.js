export function countAttended(participants = []) {
  return participants.reduce((count, person) => count + (person.attended ? 1 : 0), 0)
}

export function percentage(present, total) {
  return total ? Math.round(present / total * 100) : 0
}
