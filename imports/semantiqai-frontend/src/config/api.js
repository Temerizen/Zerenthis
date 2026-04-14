export const API_BASE = "https://semantiqai-backend-production.up.railway.app"

async function parseResponse(response) {
  const text = await response.text()

  try {
    const data = JSON.parse(text)
    if (!response.ok) {
      throw new Error(data.error || "Request failed.")
    }
    return data
  } catch (err) {
    if (!response.ok) {
      throw new Error(text || "Backend returned invalid response.")
    }
    throw new Error("Backend returned non-JSON response.")
  }
}

export async function apiGet(path = "/") {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  })
  return parseResponse(response)
}

export async function apiPost(path = "/", body = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  })
  return parseResponse(response)
}

export async function founderGet(path = "/", founderKey = "") {
  const headers = {
    "Content-Type": "application/json"
  }

  if (founderKey) {
    headers["x-founder-key"] = founderKey
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers
  })
  return parseResponse(response)
}

export async function founderPost(path = "/", body = {}, founderKey = "") {
  const headers = {
    "Content-Type": "application/json"
  }

  if (founderKey) {
    headers["x-founder-key"] = founderKey
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
  return parseResponse(response)
}
