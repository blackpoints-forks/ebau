import Route from "@ember/routing/route";
import { inject as service } from "@ember/service";

export default class OrganisationRoute extends Route {
  @service shoebox;

  model() {
    return this.shoebox.content.serviceId;
  }
}
