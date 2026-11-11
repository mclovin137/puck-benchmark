FROM maven:3.9.11-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -q dependency:go-offline
COPY src src
RUN mvn -q package -DskipTests
FROM eclipse-temurin:21-jre
WORKDIR /app
RUN groupadd -r finance && useradd -r -g finance finance
COPY --from=build /app/target/c4-finance-0.1.0.jar app.jar
USER finance
EXPOSE 18084
ENTRYPOINT ["java","-jar","app.jar"]
