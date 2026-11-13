package com.puck.finance;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonMappingException;
import java.io.IOException;
public class DecimalString extends JsonDeserializer<String> {
 @Override public String deserialize(JsonParser parser, DeserializationContext context) throws IOException {
  if (!parser.hasToken(JsonToken.VALUE_STRING)) throw JsonMappingException.from(parser,"Valor deve ser texto decimal");
  return parser.getText();
 }
}
