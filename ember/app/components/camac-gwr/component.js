import CamacInputComponent from "citizen-portal/components/camac-input/component";
import CamacMultipleQuestionMixin from "citizen-portal/mixins/camac-multiple-question";

export default class CamacGwrComponent extends CamacInputComponent.extend(
  CamacMultipleQuestionMixin,
  {}
) {}
