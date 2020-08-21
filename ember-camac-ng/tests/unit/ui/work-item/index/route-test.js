import { setupTest } from "ember-qunit";
import { module, test } from "qunit";

module("Unit | Route | work-item.index", function(hooks) {
  setupTest(hooks);

  test("it exists", function(assert) {
    const route = this.owner.lookup("route:work-item.index");
    assert.ok(route);
  });
});
