import Controller from "@ember/controller";
import { inject as service } from "@ember/service";
import { computed } from "@ember/object";

export default Controller.extend({
  questionStore: service("question-store"),

  questionActive: computed("model.instance.fields.@each", function() {
    return (
      this.get("model.meta.editable").includes("form") &&
      this.get("model.instance.fields").findBy("name", "bauherrschaft")
    );
  }),

  actions: {
    async copyQuestionValue() {
      let question = await this.questionStore.peek(
        "projektverfasser-planer",
        this.get("model.instance.id")
      );
      question.set(
        "model.value",
        question
          .getWithDefault("model.value", [])
          .pushObjects(this.bauherrschaftValue)
          .uniqBy("uuid")
      );
      await this.get("questionStore.saveQuestion").perform(question);
    }
  }
});
