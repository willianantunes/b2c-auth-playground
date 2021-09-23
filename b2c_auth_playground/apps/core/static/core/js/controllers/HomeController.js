import { $ } from "../utils/dom"
import { consultUserData, consultWhatBackendHas } from "../services/oidc-api"

export class HomeController {
  constructor() {
    // Buttons
    this._buttonSeeYourData = $(".btn-see-your-data")
    this._buttonSeeYourBackendData = $(".btn-see-your-backend-data")
    // Events
    this._initAllEvents()
  }

  _initAllEvents() {
    if (this._buttonSeeYourData) this._buttonSeeYourData.addEventListener("click", e => this.consultUserData(e))
    if (this._buttonSeeYourBackendData)
      this._buttonSeeYourBackendData.addEventListener("click", e => this.consultWhatBackendHas(e))
  }

  async consultUserData(event) {
    event.preventDefault()
    const result = await consultUserData()
    console.log(result)
    alert("See your browser's console!")
  }

  async consultWhatBackendHas(event) {
    event.preventDefault()
    const result = await consultWhatBackendHas()
    console.log(result)
    alert("See your browser's console!")
  }
}
