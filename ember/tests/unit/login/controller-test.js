import { moduleFor, test } from 'ember-qunit'

moduleFor('controller:login', 'Unit | Controller | login', {
  // Specify the other units that are required for this test.
  needs: ['service:session']
})

// Replace this with your real tests.
test('it exists', function(assert) {
  let controller = this.subject()
  assert.ok(controller)
})
