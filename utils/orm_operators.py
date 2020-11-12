from itertools import islice


class BulkBatchManager:
    """A class to use django orm bulk method by batches

    This class provide a way to make bulk db operations like bulk creating
    or bulk updating given a certain batch size, in order to reduce the
    memory cost in Python and the DB, and increase the speed of the operation

    Attributes
    ----------
    _model: django.db.models.Model object
        The model object to use for the bulk operations
    _batch_size: Integer
        The batch size to use for the bulk operations
    _ignore_conflicts: bool
        Use ignore_conflicts on bulk_create calls
    _logger: logging.Logger object
        The logger to use when logging batch steps

    Methods
    -------
    bulk_create(generator)
        Batch bulk create from a generator
    bulk_create_or_update(generator, fields)
        Batch bulk create or update from a generator and a list of fields
    """

    def __init__(self, model, batch_size=10000, ignore_conflicts=False,
                 logger=None):
        self._model = model
        self._batch_size = batch_size
        self._ignore_conflicts = ignore_conflicts
        self._logger = logger

    def bulk_create(self, generator):
        """Batch bulk create from a generator
        """
        while True:

            items = list(islice(generator, self._batch_size))
            if not items:
                break
            self._model.objects.bulk_create(
                items, ignore_conflicts=self._ignore_conflicts)

            if self._logger:
                self._logger.info(
                    "Bulk created new batch of %s %s instances"
                    % (len(items), self._model.__name__))

    def bulk_update_or_create(self, generator, fields):
        """Batch bulk update or create from a generator and a list of fields
        """
        while True:

            items = list(islice(generator, self._batch_size))
            if not items:
                break
            # Bulk get or create by creating the new then updating the existing
            self._model.objects.bulk_create(
                items, ignore_conflicts=self._ignore_conflicts)
            self._model.objects.bulk_update(items, fields)

            if self._logger:
                self._logger.info(
                    "Bulk updated or created new batch of %s %s instances"
                    % (len(items), self._model.__name__))
