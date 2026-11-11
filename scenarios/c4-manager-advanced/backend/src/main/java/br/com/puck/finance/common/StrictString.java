package br.com.puck.finance.common;
import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import java.io.IOException;
/** O contrato monetário exige string decimal, sem coerção de Number JSON. */
public class StrictString extends JsonDeserializer<String> {
 @Override public String deserialize(JsonParser p,DeserializationContext c)throws IOException{
  if(p.currentToken()!=JsonToken.VALUE_STRING)return (String)c.handleUnexpectedToken(String.class,p);
  return p.getText();
 }
}
