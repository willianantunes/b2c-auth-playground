import {$} from "../utils/dom"
import {consultUserData, consultWhatBackendHas} from "../services/oidc-api";

export class HomeController {
    constructor() {
        // All inputs
        // this._inputTextToBeTranscribed = $("textarea[name=text-to-be-transcribed]")
        // this._inputPitch = $("input[name=pitch]")
        // Buttons
        this._buttonSeeYourData = $(".btn-see-your-data")
        this._buttonSeeYourBackendData = $(".btn-see-your-backend-data")
        // Values
        // this._pitchValue = $(".pitch-value")
        // Events
        this._initAllEvents()
    }

    _initAllEvents() {
        this._buttonSeeYourData.addEventListener("click", (e) => this.consultUserData(e))
        this._buttonSeeYourBackendData.addEventListener("click", (e) => this.consultWhatBackendHas(e))
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
