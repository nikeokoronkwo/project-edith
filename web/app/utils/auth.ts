import { createAuthClient } from "better-auth/vue"
import { jwtClient } from "better-auth/client/plugins"

export const authClient = createAuthClient({
  plugins: [
    jwtClient()
  ]
})