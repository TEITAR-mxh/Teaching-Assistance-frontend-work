import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// FontAwesome imports
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faInfoCircle,
  faListAlt,
  faBook,
  faFilePowerpoint,
  faUserCircle,
  faCircle,
  faClock,
  faCheckCircle,
  faExclamationTriangle,
  faArrowRight,
  faSitemap,
  faClipboardCheck
} from '@fortawesome/free-solid-svg-icons'

// Add icons to the library
library.add(faInfoCircle, faListAlt, faBook, faFilePowerpoint, faUserCircle, faCircle, faClock, faCheckCircle, faExclamationTriangle, faArrowRight, faSitemap, faClipboardCheck)

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.component('font-awesome-icon', FontAwesomeIcon) // Register the component globally
app.mount('#app')
