![swiftmovers Dashboard](https://user-images.githubusercontent.com/44495184/185379472-2a204c0b-9b7a-4a3e-93c0-2cb85205ed5e.png)

<div align="center">
  <h1>swiftmovers Dashboard</h1>
</div>

<div align="center">
  <p>A GraphQL-powered, single-page dashboard application for <a href="https://github.com/swiftmovers/swiftmovers">swiftmovers</a>.</p>
</div>

<div align="center">
  <a href="https://swiftmovers.io/">🏠 Website</a>
  <span> • </span>
  <a href="https://docs.swiftmovers.io/docs/3.x/">📚 Docs</a>
  <span> • </span>
  <a href="https://swiftmovers.io/blog/">📰 Blog</a>
  <span> • </span>
  <a href="https://twitter.com/getswiftmovers">🐦 Twitter</a>
</div>

<div align="center">
  <a href="https://demo.swiftmovers.io/dashboard">▶️ Demo</a>
   <span> • </span>
  <a href="https://githubbox.com/swiftmovers/swiftmovers-dashboard">🔎 Explore Code</a>
</div>

## Prerequisites

- Node.js v18+
- A running instance of [swiftmovers](https://github.com/swiftmovers/swiftmovers/)

## Development

1. Clone the repository:

```bash
git clone https://github.com/swiftmovers/swiftmovers-dashboard.git
```

2. Enter the project directory:

```bash
cd swiftmovers-dashboard
```

3. Install the dependencies:

```bash
npm i
```

4. Configure the env vars as described in [docs/configuration.md](docs/configuration.md).

5. Start the development server with:

```bash
npm run dev
```

> Note:
> If you see CORS errors, check [CORS configuration](https://docs.swiftmovers.io/docs/3.x/developer/running-swiftmovers/configuration#allowed_client_hosts) of your swiftmovers instance or CORS settings in the Cloud Console.

## Docs

- [Configuration ⚙️](docs/configuration.md)
- [Error tracking ⚠️](docs/error-tracking.md)
- [Running tests 🏁](docs/running-tests.md)
- [Usage with Docker 🐳](docs/docker.md)
- [Sentry adapter 🗼](docs/sentry-adapter.md)
- [Deployment 🌐](docs/deployment.md)
