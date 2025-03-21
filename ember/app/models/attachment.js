import Model, { attr, belongsTo, hasMany } from "@ember-data/model";
import { inject as service } from "@ember/service";
import computedTask from "citizen-portal/lib/computed-task";
import { task } from "ember-concurrency";
import fetch from "fetch";

export default Model.extend({
  name: attr("string"),
  path: attr("string"),
  date: attr("date"),
  mimeType: attr("string"),
  question: attr("string"),
  instance: belongsTo("instance"),
  attachmentSections: hasMany("attachment-section"),

  session: service(),

  thumbnail: computedTask("_thumbnail", "path"),
  _thumbnail: task(function* () {
    if (!this.path) {
      return;
    }

    const response = yield fetch(`/api/v1/attachments/${this.id}/thumbnail`, {
      headers: {
        Authorization: `Bearer ${this.get(
          "session.data.authenticated.access_token"
        )}`,
      },
    });

    return yield new Promise((resolve) => {
      const fr = new FileReader();

      fr.onload = () => resolve(fr.result);

      response.blob().then((blob) => fr.readAsDataURL(blob));
    });
  }).restartable(),
});
