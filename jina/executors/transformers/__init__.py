import inspect
from typing import Dict, List

from .. import BaseExecutor


class BaseTransformer(BaseExecutor):
    """A :class:`BaseTransformer` transform the content of `Document` or `Chunk`. It can be used for preprocessing,
    segmenting etc.

    The apply function is :func:`transform`, where the name of the arguments will be used as keys of the content.

    .. seealso::
        :mod:`jina.drivers.handlers.transform`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_keys = {k for k in inspect.getfullargspec(self.transform).args if k != 'self'}
        if not self.required_keys:
            self.logger.warning('transformer works on keys, but no keys are specified')

    def transform(self, *args, **kwargs) -> Dict:
        """The apply function of this executor.

        The name of the arguments are used as keys, which are then used to tell :class:`Driver` what information to extract
        from the protobuf request accordingly. Therefore the name of the arguments should be always valid keys defined
        in the protobuf.
        """
        raise NotImplementedError


class BaseChunkTransformer(BaseTransformer):
    """:class:`BaseChunkTransformer` works on chunk-level and returns new value on chunk-level.

    The example below shows a dummy transformer add ``doc_id`` to the ``chunk_id`` and use it as the new ``chunk_id``.

    .. highlight:: python
    .. code-block:: python

        class DummyTransformer(BaseDocTransformer):
            def transform(chunk_id, doc_id):
                return {'chunk_id': doc_id + chunk_id}

    """
    pass


class BaseDocTransformer(BaseTransformer):
    """:class:`BaseDocTransformer` works on doc-level and returns new value on doc-level.

    The example below shows a dummy transformer add one to the ``doc_id`` and use it as the new ``doc_id``.

    .. highlight:: python
    .. code-block:: python

        class DummyTransformer(BaseDocTransformer):
            def transform(chunk_id, doc_id):
                return {'doc_id': doc_id + 1}

    """
    pass


class BaseSegmenter(BaseTransformer):
    """:class:`BaseSegmenter` works on doc-level,
        it receives value on the doc-level and returns new value on the chunk-level """

    def transform(self, *args, **kwargs) -> List[Dict]:
        """The apply function of this executor.

        Unlike :class:`BaseTransformer`, the :func:`transform` here works on doc-level info and the output is defined on
        chunk-level. Therefore the name of the arguments should be always valid keys defined
        in the doc-level protobuf whereas the output dict keys should always be valid keys defined in the chunk-level
        protobuf.

        :return: a list of chunks-level info represented by a dict
        """
        raise NotImplementedError
