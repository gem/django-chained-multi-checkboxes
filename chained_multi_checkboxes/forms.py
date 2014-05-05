from django import forms
from django.forms import ModelForm
from django.forms.models import ChoiceField, ModelChoiceIterator

import widgets as example_widgets

class ChainedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    self.choice(obj) for obj in self.queryset.all()
                ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for obj in self.queryset.all():
                yield self.choice(obj)


    def choice(self, obj):
        # TODO: from .group to a dynamic field
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj.group, obj.is_visible)

class ModelChainedMultipleChoiceField(forms.ModelMultipleChoiceField):

    def __init__(self, parent_field, *args, **kwargs):
        self.parent_field = parent_field
        super(ModelChainedMultipleChoiceField, self).__init__(*args, **kwargs)

    # override ModelMultipleChoiceField ->  ModelChoiceField :: _get_choices
    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices

        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. Note that we're instantiating a new ModelChoiceIterator *each*
        # time _get_choices() is called (and, thus, each time self.choices is
        # accessed) so that we can ensure the QuerySet has not been consumed. This
        # construct might look complicated but it allows for lazy evaluation of
        # the queryset.
        return ChainedModelChoiceIterator(self)

    # override ModelMultipleChoiceField ->  ModelChoiceField :: choices
    choices = property(_get_choices, ChoiceField._set_choices)

