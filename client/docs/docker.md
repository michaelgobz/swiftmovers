# Usage with Docker

Build Docker image:

```shell
docker build --tag swiftmovers-dashboard .
```

Run nginx from Docker and bind it to port on your machine (in this example, it is "8080"):

```shell
docker run --publish 8080:80 --env "API_URL=<YOUR_API_URL>" swiftmovers-dashboard
```

Enter `http://localhost:8080/` to use the dashboard.

If you want to change `API_URL` in runtime, you can use (assuming you have a running container named `swiftmovers-dashboard`):

```shell
docker exec -it -e API_URL=NEW_URL swiftmovers-dashboard /docker-entrypoint.d/50-replace-api-url.sh
```
