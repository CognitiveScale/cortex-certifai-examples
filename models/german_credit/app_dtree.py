from certifai.model.sdk import SimpleModelWrapper
import pickle

with open('german_credit_dtree.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)

app = SimpleModelWrapper(model=model, encoder=encoder)
app.run()
