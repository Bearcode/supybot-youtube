This a developer key by going to the [Developers Console](https://console.developers.google.com/project) and following these steps:

- Open the [Google Developers Console](https://console.developers.google.com/project)
- Create a new project or select an existing one
- Under "APIs & auth" -> "APIs" follow the link to "YouTube Data API" and enable the API
- Under "APIs & auth" -> "Credentials" click "Create new key" and copy the API key
- Set the key: `@config supybot.plugins.Youtube.developer_key your_developer_key_here`
- Reload: `@reload Youtube`