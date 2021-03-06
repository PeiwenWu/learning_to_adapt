import os
import sys

import numpy as np
import keras
import kaldi_io
import tensorflow as tf

from keras.models import Model
from keras.layers import Input
from learning_to_adapt.model import load_model, create_maml, create_model, create_adapter, create_model_wrapper, set_model_weights


def converted_models_produce_correct_output(m_in, m_out):
    # Test that converted models
    adapt_x = np.random.normal(size=(4, 3, 20, 78, 40))
    adapt_y = np.ones((4, 3, 20, 50, 1))
    test_x = np.random.normal(size=(4, 20, 78, 40))

    # Workaround for MAML models with wrong input dimensions
    # maml = m_in.get_layer('maml_1')
    # maml.wrapper.batch_size = 4
    # m_in = create_maml(maml.wrapper, maml.get_weights()[0], maml.num_steps, maml.use_second_order_derivatives, maml.use_lr_per_step, maml.use_kld_regularization)
    # m_in.load_weights(weights_in)

    reference_predictions = m_in.predict([adapt_x, adapt_y, test_x])[1][0]
    test_predictions = m_out.predict(test_x[0])
    return np.allclose(reference_predictions, test_predictions)

if __name__ == '__main__':
    model_in = sys.argv[1]
    weights_in = sys.argv[2]
    model_out = sys.argv[3]
    meta_out = sys.argv[4]

    if not model_in.endswith('.h5') or not model_out.endswith('.h5') or not meta_out.endswith('.h5'):
        raise TypeError ('Unsupported model type. Please use h5 format. Update Keras if needed')

    m_in = load_model(model_in)
    m_in.load_weights(weights_in)
    weights = m_in.get_weights()

    # Bugfix for wrongly saved model-wrapper
    m_in.get_layer('maml_1').wrapper.set_weights(m_in.get_layer('model_wrapper_2').get_weights())

    try:
      lda = m_in.get_layer('lda_1')
      lda_weights = [x.flatten() for x in lda.get_weights()]
    except ValueError:
      lda_weights = []
      model_weights = weights[0][0]

    maml = m_in.get_layer('maml_1')
    m_out = create_model(maml.wrapper, m_in.get_layer('lda_1'))

    model_weights = np.concatenate(lda_weights + [maml.get_weights()[0].flatten()])
    set_model_weights(m_out, model_weights, maml.wrapper)

    assert converted_models_produce_correct_output(m_in, m_out)

    m_out.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
    m_out.save(model_out)
    m_out.summary()

    adapter = create_adapter(create_model_wrapper(m_out), maml.num_steps, maml.use_lr_per_step, maml.use_kld_regularization, maml.get_weights()[1:])
    adapter.save(meta_out)
    adapter.summary()

    print maml.get_weights()[1]
