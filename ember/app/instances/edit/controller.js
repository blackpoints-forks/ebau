import Controller from '@ember/controller'
import EmberObject, { computed, get, getWithDefault } from '@ember/object'
import { inject as service } from '@ember/service'
import { task } from 'ember-concurrency'
import { all } from 'rsvp'
import { getOwner } from '@ember/application'

const Module = EmberObject.extend({
  questionStore: service(),

  allQuestions: computed('questions', 'submodules.@each.questions', function() {
    return [
      ...this.getWithDefault('questions', []),
      ...this.getWithDefault('submodules', []).reduce((qs, submodule) => {
        return [...qs, ...getWithDefault(submodule, 'questions', [])]
      }, [])
    ]
  }),

  state: computed(
    'questionStore._store.@each.{value,hidden,isNew}',
    async function() {
      let names = this.getWithDefault('allQuestions', [])

      let questions = await this.get('questionStore.findSet').perform(
        names,
        this.get('instance')
      )

      let visibles = await all(
        questions.map(async q => ((await q.get('hidden')) ? null : q))
      )

      let visibleQuestions = visibles.filter(Boolean)

      if (!visibleQuestions.length) {
        return null
      }

      if (visibleQuestions.every(q => q.get('isNew'))) {
        return 'untouched'
      }

      let relevantQuestions = visibleQuestions.filter(q =>
        q.get('field.required')
      )

      if (relevantQuestions.some(q => q.get('isNew'))) {
        return 'unfinished'
      }

      return relevantQuestions.every(q => q.validate() === true)
        ? 'valid'
        : 'invalid'
    }
  )
})

export default Controller.extend({
  router: service(),
  ajax: service(),

  config: computed(async function() {
    return await this.get('ajax').request('/api/v1/form-config')
  }),

  modules: computed('model.form.name', async function() {
    let { forms, modules } = await this.get('config')

    let usedModules = (forms[this.get('model.form.name')] || [])
      .map(name => ({ name, ...modules[name] } || null))
      .filter(Boolean)

    return usedModules
      .map(({ name, title, parent, questions }) => {
        return Module.create({
          container: getOwner(this).__container__,

          link: `instances.edit.${name}`,
          instance: this.get('model.id'),
          name,
          title,
          questions,
          parent,
          submodules: []
        })
      })
      .filter(mod => {
        try {
          this.get('router').urlFor(mod.get('link'))
          return true
        } catch (e) {
          // URL does not exist, skip this module
          return false
        }
      })
  }),

  navigation: computed('modules.[]', async function() {
    let modules = await this.get('modules')

    return modules.reduce((nav, mod) => {
      if (mod.get('parent')) {
        let parent = nav.find(n => n.get('name') === mod.get('parent'))

        parent.set('submodules', [...parent.get('submodules'), mod])
      } else {
        nav.push(mod)
      }

      return nav
    }, [])
  }),

  links: computed('modules.[]', async function() {
    let modules = await this.get('modules')

    return [
      'instances.edit',
      ...(await all(
        modules.map(async m => {
          return (await m.get('state')) ? m.get('link') : null
        })
      )).filter(Boolean),
      'instances.edit.submit'
    ]
  }),

  currentIndex: computed(
    'links.[]',
    'router.currentRouteName',
    async function() {
      let links = await this.get('links')

      return links.indexOf(
        this.get('router.currentRouteName').replace(/\.index$/, '')
      )
    }
  ),

  hasPrev: computed('currentIndex', async function() {
    return (await this.get('currentIndex')) > 0
  }),

  hasNext: computed('links.length', 'currentIndex', async function() {
    return (
      (await this.get('currentIndex')) <
      (await this.get('links')).get('length') - 1
    )
  }),

  prev: task(function*() {
    let links = yield this.get('links')
    let i = yield this.get('currentIndex')

    yield this.transitionToRoute(
      get(links, (i + links.length - 1) % links.length)
    )
  }),

  next: task(function*() {
    let links = yield this.get('links')
    let i = yield this.get('currentIndex')

    yield this.transitionToRoute(get(links, (i + 1) % links.length))
  })
})
