import { render } from "@ember/test-helpers";
import { hbs } from "ember-cli-htmlbars";
import { setupRenderingTest } from "ember-qunit";
import { module, test } from "qunit";

module("Integration | Component | be-download-pdf", function (hooks) {
  setupRenderingTest(hooks);

  test("it renders", async function (assert) {
    await render(
      hbs`<BeDownloadPdf @field={{hash question=(hash raw=(hash label="Test"))}} />`
    );

    assert.dom("button").hasText("Test");
  });
});
