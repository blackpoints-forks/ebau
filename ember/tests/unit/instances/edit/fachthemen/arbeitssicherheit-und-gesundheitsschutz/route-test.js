import { module, test } from 'qunit'
import { setupTest } from 'ember-qunit'

module(
  'Unit | Route | instances/edit/fachthemen/arbeitssicherheit-und-gesundheitsschutz',
  function(hooks) {
    setupTest(hooks)

    test('it exists', function(assert) {
      let route = this.owner.lookup(
        'route:instances/edit/fachthemen/arbeitssicherheit-und-gesundheitsschutz'
      )
      assert.ok(route)
    })
  }
)
