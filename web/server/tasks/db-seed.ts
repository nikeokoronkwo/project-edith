export default defineTask({
  meta: {
    name: 'db:seed',
    description: 'Seed database with initial users'
  },
  async run({ payload, context }) {
    const users = [
      { email: 'nick.fury@shield.gov', name: 'Nick Fury', password: 'shield123' },
      { email: 'steve.rogers@shield.gov', name: 'Steve Rogers', password: 'shield123' },
      { email: 'bruce.banner@shield.gov', name: 'Bruce Banner', password: 'shield123' },
      { email: 'natasha.romanoff@shield.gov', name: 'Natasha Romanoff', password: 'shield123' },
      { email: 'sam.wilson@shield.gov', name: 'Sam Wilson', password: 'shield123' },
    ]

    for (const user of users) {
      try {
        await auth.api.signUpEmail({
          body: {
            email: user.email,
            password: user.password,
            name: user.name,
          }
        })
        console.log(`Created user: ${user.email}`)
      } catch (e) {
        console.log(`User already exists: ${user.email}`)
      }
    }

    return {
      success: true,
      result: `Seeded ${users.length} users`
    }
  }
})
