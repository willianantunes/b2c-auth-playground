import axios from "axios"

export async function consultUserData() {
  const options = {
    method: "GET",
    timeout: 15 * 1000
  }
  options.url = "http://localhost:8000/api/v1/user-data"
  options.headers = { ...options.headers }

  const response = await axios(options)

  return await response.data
}


export async function consultWhatBackendHas() {
  const options = {
    method: "GET",
    timeout: 15 * 1000
  }
  options.url = "http://localhost:8000/api/v1/what-i-have"
  options.headers = { ...options.headers }

  const response = await axios(options)

  return await response.data
}
