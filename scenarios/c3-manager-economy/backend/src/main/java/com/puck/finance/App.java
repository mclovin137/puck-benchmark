package com.puck.finance;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.boot.autoconfigure.jackson.Jackson2ObjectMapperBuilderCustomizer;
import com.fasterxml.jackson.databind.MapperFeature;
@SpringBootApplication public class App { public static void main(String[] args){SpringApplication.run(App.class,args);} @Bean Jackson2ObjectMapperBuilderCustomizer strictJson(){return builder -> builder.featuresToDisable(MapperFeature.ALLOW_COERCION_OF_SCALARS);} }
