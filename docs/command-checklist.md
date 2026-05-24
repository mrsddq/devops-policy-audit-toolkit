# Command Checklist

## Git

```bash
git status
git checkout -b feature/name
git add .
git commit -m "message"
git push origin feature/name
```

## Docker

```bash
docker build -t app:local .
docker run --rm -p 8080:8080 app:local
docker logs <container>
```

## Kubernetes

```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl describe pod <pod>
kubectl logs <pod>
kubectl delete -f deployment.yaml
```

## Terraform

```bash
terraform fmt
terraform init
terraform validate
terraform plan
terraform apply
terraform destroy
```

## Jenkins

- Keep credentials in Jenkins credentials store.
- Use declarative pipelines for repeatability.
- Add build, test, scan, package, deploy stages.
- Archive artifacts.
- Keep deployment targets out of source code.
