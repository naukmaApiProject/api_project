helm repo add my-api-repo https://laarchenko.github.io/charts
helm install cool-app --values k8s/chart/values.yaml my-api-repo/app-project
helm ls