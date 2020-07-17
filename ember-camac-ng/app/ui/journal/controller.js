import Controller from "@ember/controller";
import { action } from "@ember/object";
import { inject as service } from "@ember/service";
import { tracked } from "@glimmer/tracking";
import { dropTask, lastValue } from "ember-concurrency-decorators";

export default class JournalController extends Controller {
  @service store;

  @tracked newEntry;
  @tracked newEntries = [];
  editText = "";

  get entries() {
    return [...(this.fetchedEntries || []).toArray(), ...this.newEntries]
      .sortBy("creationDate")
      .reverse();
  }

  @lastValue("fetchEntries") fetchedEntries;
  @dropTask
  *fetchEntries() {
    this.instance = this.store.findRecord("instance", this.model.id);

    return yield this.store.query("journal-entry", {
      instance: this.model.id,
      include: "user"
    });
  }

  @dropTask
  *saveEntry(entry) {
    yield entry.save();

    if (this.newEntry) {
      this.newEntries.pushObject(entry);
      this.newEntry = undefined;
    }

    return entry;
  }

  @action
  addNewEntry() {
    this.newEntry = this.store.createRecord("journal-entry", {
      instance: this.instance
    });
  }

  @action
  cancelNewEntry() {
    this.newEntry = undefined;
  }

  @action
  cancelEditEntry(entry) {
    entry.rollbackAttributes();
  }
}