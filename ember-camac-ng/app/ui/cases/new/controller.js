import Controller from "@ember/controller";
import { inject as service } from "@ember/service";
import { tracked } from "@glimmer/tracking";
import calumaQuery from "ember-caluma/caluma-query";
import { allForms } from "ember-caluma/caluma-query/queries";
import {
  restartableTask,
  dropTask,
  lastValue,
} from "ember-concurrency-decorators";

import ENV from "camac-ng/config/environment";

export default class CasesNewController extends Controller {
  @service fetch;
  @service router

  @tracked selectedForm = null;

  @calumaQuery({ query: allForms })
  formQuery;

  @lastValue("fetchForms") forms;
  @restartableTask
  *fetchForms() {
    yield this.formQuery.fetch({
      filter: [
        { isPublished: true },
        { isArchived: false },
        { orderBy: "NAME_ASC" },
      ],
    });
  }

  @dropTask
  *createCase() {
    const body = {
      data: {
        attributes: {
          "caluma-form": this.selectedForm,
        },
        type: "instances",
      },
    };

    if (ENV.APPLICATION.newCase.calumaWorkflow) {
      body.data.attributes["caluma-workflow"] =
        ENV.APPLICATION.newCase.calumaWorkflow;
    }
    if (ENV.APPLICATION.newCase.camacForm) {
      body.data.relationships = {
        form: {
          data: {
            id: ENV.APPLICATION.newCase.camacForm,
            type: "forms",
          },
        },
      };
    }

    yield this.fetch.fetch(`/api/v1/instances`, {
      method: "POST",
      body: JSON.stringify(body),
    });

    // TODO transition to list resource
  }
}
