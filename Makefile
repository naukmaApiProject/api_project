build:
	docker build . -t vampir/api-app
push-image:
	docker push vampir/api-app
install:
	helm install cool-app k8s/chart/
uninstall:
	helm uninstall cool-app
