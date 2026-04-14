import { useEffect, useState } from 'react'
import { apiGet } from '../config/api'

export function usePlatformStatus() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true

    async function run() {
      try {
        const result = await apiGet('/status')
        if (alive) setStatus(result)
      } finally {
        if (alive) setLoading(false)
      }
    }

    run()
    return () => { alive = false }
  }, [])

  return { status, loading }
}
