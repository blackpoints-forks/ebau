import Model, { attr, belongsTo } from "@ember-data/model";

export default Model.extend({
  name: attr("string"),
  value: attr(),
  instance: belongsTo("instance"),
});
