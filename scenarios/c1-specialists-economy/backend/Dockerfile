FROM eclipse-temurin:21-jre
WORKDIR /app
COPY target/finance-api-0.1.0.jar app.jar
EXPOSE 8080
USER 10001:10001
ENTRYPOINT ["java","-jar","/app/app.jar"]
