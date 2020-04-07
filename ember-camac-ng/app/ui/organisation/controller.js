import Controller from "@ember/controller";
import { inject as service } from "@ember/service";
import { loadingTask } from "camac-ng/decorators";
import Changeset from "ember-changeset";
import { dropTask, lastValue } from "ember-concurrency-decorators";

export default class OrganisationController extends Controller {
  @service intl;
  @service notifications;
  @service store;

  @lastValue("fetchService") service;
  @dropTask
  @loadingTask
  *fetchService() {
    const service = yield this.store.findRecord("service", this.model);

    return new Changeset(service);
  }

  @dropTask
  @loadingTask
  *save(event) {
    event.preventDefault();

    try {
      this.service.set("description", this.service.name);

      yield this.service.save();

      this.notifications.success(this.intl.t("organisation.saveSuccess"));
    } catch (error) {
      this.notifications.error(this.intl.t("organisation.saveError"));
    }
  }
}