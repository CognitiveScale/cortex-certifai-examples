from certifai.common.hosted_model import IHostedModel

class SkLearnSoftWrapper(IHostedModel):
    def __init__(self, skl_model):
        self.skl_model = skl_model

    def predict(self, x):
        return self.skl_model.predict(x)

    def soft_predict(self, x):
        return self.skl_model.predict_proba(x)

