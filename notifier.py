from discordwebhook import Discord

discord = Discord(url='https://discord.com/api/webhooks/1220885779690164334/tqr5OoTax9c0phi6js4u948huYh9RCZPwTyUK-RCzC7__tebWedWjFViTy3jCuBGYymE')

def notification(message):
    discord.post(content=message)