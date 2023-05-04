## Run

Helm way
* to install ```helm install cool-app k8s/chart```
* to uninstall ```helm delete cool-app```

K8s way
* to install ```kubectl apply -f k8s/bare/app.yaml; kubectl apply -f k8s/bare/app-service.yaml;```
* to uninstall ```kubectl delete -f k8s/bare/app.yaml; kubectl delete -f k8s/bare/app-service.yaml;```

Docker way
* to run ```docker run -p 5000:5000 vampir/api-app```

P.S. Dont forget to apply env vars first !
