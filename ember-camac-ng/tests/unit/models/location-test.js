import { setupTest } from "ember-qunit";
import { module, test } from "qunit";

module("Unit | Model | location", function (hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test("it exists", function (assert) {
    const store = this.owner.lookup("service:store");
    const model = store.createRecord("location", {});
    assert.ok(model);
  });
});
