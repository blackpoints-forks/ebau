import Route from "@ember/routing/route";
import { inject as service } from "@ember/service";
import { task } from "ember-concurrency";
import getCaseQuery from "ember-caluma-portal/gql/queries/get-case";

export default Route.extend({
  apollo: service(),
  notification: service(),

  model({ case_id }) {
    console.log("model", case_id);
    return this.get("data").perform(case_id);
  },

  data: task(function*(caseId) {
    try {
      return yield this.get("apollo").watchQuery(
        {
          query: getCaseQuery,
          fetchPolicy: "cache-and-network",
          variables: { caseId }
        },
        "node"
      );
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error(e);
      this.get("notification").danger(
        this.get("intl").t("global.loadingError")
      );
    }
  }).restartable()
});
