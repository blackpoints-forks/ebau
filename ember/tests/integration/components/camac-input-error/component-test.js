import { render } from "@ember/test-helpers";
import { setupRenderingTest } from "ember-qunit";
import hbs from "htmlbars-inline-precompile";
import { module, test } from "qunit";

module("Integration | Component | camac-input-error", function (hooks) {
  setupRenderingTest(hooks);

  test("it renders errors correctly", async function (assert) {
    this.set("error", []);

    await render(hbs`{{camac-input-error error}}`);

    assert.dom("ul").doesNotExist();
    assert.dom("li").doesNotExist();

    this.set("error", ["wrong", "more wrong"]);

    assert.dom("ul").exists();
    assert.dom("li").exists({ count: 2 });
  });
});
