import { setupTest } from "ember-qunit";
import { module, test } from "qunit";

module("Unit | Route | logout", function (hooks) {
  setupTest(hooks);

  test("it exists", function (assert) {
    const route = this.owner.lookup("route:logout");
    assert.ok(route);
  });
});
