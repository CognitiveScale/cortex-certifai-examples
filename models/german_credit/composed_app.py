from certifai.model.sdk import SimpleModelWrapper, ComposedModelWrapper
import pickle
with open('german_credit_dtree.pkl', 'rb') as f:
    saved = pickle.load(f)
    dtree_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

with open('german_credit_logit.pkl', 'rb') as f:
    saved = pickle.load(f)
    logit_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

with open('german_credit_mlp.pkl', 'rb') as f:
    saved = pickle.load(f)
    mlp_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

with open('german_credit_svm.pkl', 'rb') as f:
    saved = pickle.load(f)
    svm_app = SimpleModelWrapper(
        model=saved.get('model'),
        encoder=saved.get('encoder', None)
    )

composed_app = ComposedModelWrapper()
composed_app.add_wrapped_model('/german_credit_dtree', dtree_app)
composed_app.add_wrapped_model('/german_credit_logit', logit_app)
composed_app.add_wrapped_model('/german_credit_svm', svm_app)
composed_app.add_wrapped_model('/german_credit_mlp', mlp_app)
composed_app.run()
