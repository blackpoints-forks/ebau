import { action } from "@ember/object";
import { inject as service } from "@ember/service";
import { htmlSafe } from "@ember/template";
import Component from "@glimmer/component";
import { useCalumaQuery } from "@projectcaluma/ember-core/caluma-query";
import { allCases } from "@projectcaluma/ember-core/caluma-query/queries";
import { DateTime } from "luxon";

import caseModelConfig from "camac-ng/config/case-model";
import caseTableConfig from "camac-ng/config/case-table";

export default class CaseTableComponent extends Component {
  @service store;
  @service intl;
  @service shoebox;

  casesQuery = useCalumaQuery(this, allCases, () => ({
    options: {
      pageSize: caseTableConfig.pageSize || 15,
      processNew: (cases) => this.processNew(cases),
    },
    ...this.gqlOrder,
    filter: this.gqlFilter,
    queryOptions: {
      context: {
        headers: {
          ...this.camacFilter,
          ...this.camacOrder,
        },
      },
    },
  }));

  get isService() {
    return this.shoebox.baseRole === "service";
  }

  get gqlOrder() {
    if (this.args.casesBackend === "caluma") {
      const order = caseTableConfig.order
        ? caseTableConfig.order[this.args.casesBackend] ?? caseTableConfig.order
        : null;
      return order ? { order } : {};
    }

    return {};
  }

  get camacOrder() {
    if (this.args.casesBackend === "camac-ng") {
      const order = caseTableConfig.order?.[this.args.casesBackend];
      return order ? { "x-camac-order": order.join(",") } : {};
    }

    return {};
  }

  get gqlFilter() {
    const filter = this.args.filter;
    const availableFilterSet = {
      buildingPermitType: {
        hasAnswer: [
          {
            question: "form-type",
            lookup: "IN",
            value: filter.buildingPermitType,
          },
        ],
      },
      instanceId: {
        metaValue: [
          {
            key: "camac-instance-id",
            value: filter.instanceId,
          },
        ],
      },
      dossierNumber: {
        metaValue: [
          {
            key: "dossier-number",
            lookup: "ICONTAINS",
            value: filter.dossierNumber,
          },
        ],
      },
      dossierNumberSZ: {
        metaValue: [
          {
            key: "dossier-number",
            lookup: "ICONTAINS",
            value: filter.dossierNumberSZ,
          },
        ],
      },
      createdBefore: {
        metaValue: [
          {
            key: "submit-date",
            lookup: "LTE",
            value: DateTime.fromISO(filter.createdBefore).endOf("day").toISO(),
          },
        ],
      },
      createdAfter: {
        metaValue: [
          {
            key: "submit-date",
            lookup: "GTE",
            value: DateTime.fromISO(filter.createdAfter).startOf("day").toISO(),
          },
        ],
      },
      intent: {
        searchAnswers: [
          {
            questions: caseModelConfig.intentSlugs,
            lookup: "CONTAINS",
            value: filter.intent,
          },
        ],
      },
      applicantName: {
        searchAnswers: [
          {
            questions: ["first-name", "last-name", "juristic-person-name"],
            lookup: "CONTAINS",
            value: filter.applicantName,
          },
        ],
      },
      street: {
        searchAnswers: [
          {
            questions: ["parcel-street", "street-number", "parcel-city"],
            lookup: "CONTAINS",
            value: filter.street,
          },
        ],
      },
      parcelNumber: {
        searchAnswers: [
          {
            questions: ["parcel-number", "building-law-number"],
            lookup: "CONTAINS",
            value: filter.parcelNumber,
          },
        ],
      },
      caseStatus: {
        status: filter.caseStatus,
      },
      caseDocumentFormName: {
        documentForm: filter.caseDocumentFormName,
      },
    };

    const searchFilters = Object.entries(filter)
      .filter(
        ([key, value]) => Boolean(value) && Boolean(availableFilterSet[key])
      )
      .map(([key]) => availableFilterSet[key]);

    const workflow = this.args.workflow;
    const excludeWorkflow = this.args.excludeWorkflow;
    return [
      ...searchFilters,
      ...(workflow ? [{ workflow }] : []),
      ...(excludeWorkflow ? [{ workflow: excludeWorkflow, invert: true }] : []),
    ];
  }

  get camacFilter() {
    const filters = {
      instance_state:
        this.args.filter.instanceState ||
        this.args.filter.instanceStateDescription ||
        this.args.instanceStates ||
        "",
      location: this.args.filter.municipality || this.args.filter.locationSZ,
      service: this.args.filter.service || this.args.filter.serviceSZ,
      responsible_service_user: this.args.filter.responsibleServiceUser,
      address_sz: this.args.filter.addressSZ,
      intent_sz: this.args.filter.intentSZ,
      plot_sz: this.args.filter.plotSZ,
      builder_sz: this.args.filter.builderSZ,
      landowner_sz: this.args.filter.landownerSZ,
      applicant_sz: this.args.filter.applicantSZ,
      submit_date_after_sz: this.args.filter.submitDateAfterSZ,
      submit_date_before_sz: this.args.filter.submitDateBeforeSZ,
      form_name_versioned: this.args.filter.formSZ,
      circulation_state: this.args.hasActivation
        ? caseTableConfig.activeCirculationStates
        : null,
      has_pending_billing_entry: this.args.hasPendingBillingEntry,
      has_pending_sanction: this.args.hasPendingSanction,
      pending_sanctions_control_instance:
        this.args.filter.pendingSanctionsControlInstance,
      with_cantonal_participation: this.args.filter.withCantonalParticipation,
      identifier: this.args.filter.instanceIdentifier || "",
      exclude_child_cases: true,
    };

    return {
      "x-camac-filters": Object.entries(filters)
        .filter(([, value]) => ![null, undefined, ""].includes(value))
        .map((entry) => entry.join("="))
        .join("&"),
    };
  }

  get paginationInfo() {
    return htmlSafe(
      this.intl.t("global.paginationInfo", {
        count: this.casesQuery.value.length,
        total: this.casesQuery.totalCount,
      })
    );
  }

  async processNew(cases) {
    if (!cases.length) {
      return [];
    }
    const instanceIds = cases.map((_case) => _case.meta["camac-instance-id"]);

    if (this.isService) {
      await this.store.query("activation", {
        instance: instanceIds.join(","),
        service: this.shoebox.content.serviceId,
        include: "circulation",
      });

      await this.store.query("responsible-service", {
        include: "responsible_user",
        instance: instanceIds.join(","),
      });
    }

    await this.store.query("instance", {
      instance_id: instanceIds.join(","),
      include: "instance_state,user,form,circulation_initializer_services",
    });

    if (this.args.casesBackend === "camac-ng") {
      await this.store.query("form-field", {
        instance: instanceIds.join(","),
        name: (caseTableConfig.formFields ?? []).join(","),
        include: "instance",
      });
    }

    return cases;
  }

  get tableColumns() {
    const tableColumns = caseTableConfig.columns[this.args.casesBackend];

    if (Array.isArray(tableColumns)) {
      return tableColumns;
    }

    return tableColumns[this.shoebox.baseRole] ?? tableColumns.default ?? [];
  }

  @action
  redirectToCase(caseRecord) {
    location.assign(
      `/index/redirect-to-instance-resource/instance-id/${caseRecord.instanceId}/`
    );
  }
}
