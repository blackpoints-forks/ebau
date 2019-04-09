import { module, test } from "qunit";
import { setupRenderingTest } from "ember-qunit";
import { render } from "@ember/test-helpers";
import hbs from "htmlbars-inline-precompile";

module("Integration | Helper | table-label", function(hooks) {
  setupRenderingTest(hooks);

  test("it works", async function(assert) {
    this.set("obj", { "table-label": "Hello", label: "Bye" });

    await render(hbs`{{table-label obj}}`);

    assert.dom(this.element).hasText("Hello");
  });

  test("it displays fallback", async function(assert) {
    this.set("obj", { label: "Bye" });

    await render(hbs`{{table-label obj}}`);

    assert.dom(this.element).hasText("Bye");
  });
});
