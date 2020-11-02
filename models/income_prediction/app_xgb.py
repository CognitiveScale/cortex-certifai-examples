from certifai.model.sdk import SimpleModelWrapper
import pickle


class Wrapper(SimpleModelWrapper):
    def set_global_imports(self):
        """
        overridden method to make external global imports
        When using external imports override the method to provide necessary imports. Make sure to mark them `global` to
        be used by certifai interpreter correctly. set once,use throughout.
        :return: None
        """
        global xgb
        import xgboost as xgb

    def soft_predict(self, npinstances):
        # reference model by using `self.model`
        return self.model.predict(xgb.DMatrix(data=npinstances))


with open('adult_income_xgb.pkl', 'rb') as f:
    saved = pickle.load(f)
    model = saved.get('model')
    encoder = saved.get('encoder', None)

if __name__ == "__main__":
    # since xgboost is a soft-scoring model with single score for each prediction,
    # we override `soft_predict` and provide `threshold` and `score_labels` to get thresholded predictions

    # Host is set to 0.0.0.0 to allow this to be run in a docker container
    app = Wrapper(host="0.0.0.0",
                  supports_soft_scores=True,
                  model=model,
                  encoder=encoder,
                  threshold=0.46,
                  score_labels=[0, 1])
    app.run(log_level="warning", production=True, num_workers=3)
