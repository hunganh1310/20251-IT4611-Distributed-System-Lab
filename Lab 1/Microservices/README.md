# Microservices Demo

A simple Kubernetes microservices architecture with API Gateway pattern.

## Architecture

![Architecture](img/image.png)

## Services

| Service | Endpoint | Port |
|---------|----------|------|
| Users | `/users` | 80 |
| Catalog | `/catalog` | 80 |
| Orders | `/orders` | 80 |

## Components

- **Gateway Ingress** - NGINX Ingress routing requests to services via `micro.local`
- **Users Service** - User management microservice
- **Catalog Service** - Product catalog microservice
- **Orders Service** - Order processing microservice

## Deployment

```bash
# Apply all manifests
kubectl apply -f users-deploy.yaml
kubectl apply -f catalog-deploy.yaml
kubectl apply -f orders-deploy.yaml
kubectl apply -f gateway-ingress.yaml

# Add host entry
echo "127.0.0.1 micro.local" >> /etc/hosts
```

## Access

- Users: `http://micro.local/users`
- Catalog: `http://micro.local/catalog`
- Orders: `http://micro.local/orders`
