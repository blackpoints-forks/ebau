import Controller from "@ember/controller";
import ENV from "citizen-portal/config/environment";
import calumaQuery from "ember-caluma/caluma-query";
import { allWorkItems } from "ember-caluma/caluma-query/queries";
import { dropTask } from "ember-concurrency-decorators";

export default class IndexController extends Controller {
  @calumaQuery({
    query: allWorkItems,
    options: {},
  })
  workItemsQuery;

  @dropTask
  *fetchWorkItems() {
    const filter = [{ status: "READY" }, { addressedGroups: ["applicant"] }];

    yield this.workItemsQuery.fetch({
      filter: [...filter],
    });
  }

  get showPublications() {
    return ENV.APP.showPublications;
  }
}
