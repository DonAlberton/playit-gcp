PREFIX="europe-central2-docker.pkg.dev/playground-454021/playit"

# docker build -t ${PREFIX}/classifier ./classifier
# docker build -t ${PREFIX}/scheduler ./scheduler
# docker build -t ${PREFIX}/playit_api ./playit_api
docker build -t ${PREFIX}/playit_api_gateway ./playit_api_gateway

# docker push ${PREFIX}/classifier
# docker push ${PREFIX}/scheduler
# docker push ${PREFIX}/playit_api
docker push ${PREFIX}/playit_api_gateway