import EmberObject, { computed, getWithDefault } from "@ember/object";
import { inject as service } from "@ember/service";
import { reads } from "@ember/object/computed";
import filesize from "filesize";
import moment from "moment";
import { task } from "ember-concurrency";
import { saveAs } from "file-saver";

export default EmberObject.extend({
  fetch: service(),
  notification: service(),
  intl: service(),

  name: reads("attributes.name"),
  path: reads("attributes.path"),
  size: computed("attributes.size", function() {
    return filesize(this.attributes.size);
  }),
  date: computed("attributes.date", function() {
    return moment(this.attributes.date);
  }),

  tags: computed("attributes.context.tags", function() {
    return getWithDefault(this, "attributes.context.tags", []).map(
      slug => this.document.findField(`root.6-dokumente.${slug}`).question.label
    );
  }),

  download: task(function*() {
    try {
      let response = yield this.fetch.fetch(`${this.path}`, {
        mode: "cors",
        headers: {
          accept: undefined,
          "content-type": undefined
        }
      });

      let file = yield response.blob();

      saveAs(file, this.name, { type: file.type });

      this.notification.success(this.intl.t("documents.downloadSuccess"));
    } catch (e) {
      /* eslint-disable-next-line no-console */
      console.error(e);
      this.notification.danger(this.intl.t("documents.downloadError"));
    }
  })
});
