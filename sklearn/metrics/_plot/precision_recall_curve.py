from .. import average_precision_score
from .. import precision_recall_curve
from ...utils._plotting import _BinaryClassifierCurveDisplayMixin
from .uncertainty import compute_sampling_uncertainty, plot_sampling_uncertainty


class PrecisionRecallDisplay(_BinaryClassifierCurveDisplayMixin):
    """Precision Recall visualization.

    It is recommend to use
    :func:`~sklearn.metrics.PrecisionRecallDisplay.from_estimator` or
    :func:`~sklearn.metrics.PrecisionRecallDisplay.from_predictions` to create
    a :class:`~sklearn.metrics.PredictionRecallDisplay`. All parameters are
    stored as attributes.

    Read more in the :ref:`User Guide <visualizations>`.

    Parameters
    ----------
    precision : ndarray
        Precision values.

    recall : ndarray
        Recall values.

    average_precision : float, default=None
        Average precision. If None, the average precision is not shown.

    estimator_name : str, default=None
        Name of estimator. If None, then the estimator name is not shown.

    pos_label : str or int, default=None
        The class considered as the positive class. If None, the class will not
        be shown in the legend.

        .. versionadded:: 0.24

    sampling_uncertainty : list of tuples (RX, RY, chi2), default=None
        The sampling uncertainty for each point on the curve.
        see more in :meth:`sklearn.metrics._plot.uncertainty.compute_sampling_uncertainty`

        .. versionadded:: 1.2.3

    Attributes
    ----------
    line_ : matplotlib Artist
        Precision recall curve.

    ax_ : matplotlib Axes
        Axes with precision recall curve.

    figure_ : matplotlib Figure
        Figure containing the curve.

    See Also
    --------
    precision_recall_curve : Compute precision-recall pairs for different
        probability thresholds.
    PrecisionRecallDisplay.from_estimator : Plot Precision Recall Curve given
        a binary classifier.
    PrecisionRecallDisplay.from_predictions : Plot Precision Recall Curve
        using predictions from a binary classifier.

    Notes
    -----
    The average precision (cf. :func:`~sklearn.metrics.average_precision`) in
    scikit-learn is computed without any interpolation. To be consistent with
    this metric, the precision-recall curve is plotted without any
    interpolation as well (step-wise style).

    You can change this style by passing the keyword argument
    `drawstyle="default"` in :meth:`plot`, :meth:`from_estimator`, or
    :meth:`from_predictions`. However, the curve will not be strictly
    consistent with the reported average precision.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from sklearn.datasets import make_classification
    >>> from sklearn.metrics import (precision_recall_curve,
    ...                              PrecisionRecallDisplay)
    >>> from sklearn.model_selection import train_test_split
    >>> from sklearn.svm import SVC
    >>> X, y = make_classification(random_state=0)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y,
    ...                                                     random_state=0)
    >>> clf = SVC(random_state=0)
    >>> clf.fit(X_train, y_train)
    SVC(random_state=0)
    >>> predictions = clf.predict(X_test)
    >>> precision, recall, _ = precision_recall_curve(y_test, predictions)
    >>> disp = PrecisionRecallDisplay(precision=precision, recall=recall)
    >>> disp.plot()
    <...>
    >>> plt.show()
    """

    def __init__(
        self,
        precision,
        recall,
        *,
        average_precision=None,
        estimator_name=None,
        pos_label=None,
        sampling_uncertainty=None,
    ):
        self.estimator_name = estimator_name
        self.precision = precision
        self.recall = recall
        self.average_precision = average_precision
        self.pos_label = pos_label
        self.sampling_uncertainty = sampling_uncertainty

    def plot(self, ax=None, *, name=None, plot_uncertainty=False, **kwargs):
        """Plot visualization.

        Extra keyword arguments will be passed to matplotlib's `plot`.

        Parameters
        ----------
        ax : Matplotlib Axes, default=None
            Axes object to plot on. If `None`, a new figure and axes is
            created.

        name : str, default=None
            Name of precision recall curve for labeling. If `None`, use
            `estimator_name` if not `None`, otherwise no labeling is shown.

        plot_uncertainty : bool, default=False
           Plot sampling uncertainty.

            .. versionadded:: 1.2.3

        uncertainty_n_std : int, default=None
           Number of standard deviation to plot for sampling uncertainty level.
           Relevant only if plot_uncertainty = True.
           see more in :meth:`sklearn.metrics._plot.uncertainty.plot_sampling_uncertainty`

            .. versionadded:: 1.2.3

        **kwargs : dict
            Keyword arguments to be passed to matplotlib's `plot`.

        Returns
        -------
        display : :class:`~sklearn.metrics.PrecisionRecallDisplay`
            Object that stores computed values.

        Notes
        -----
        The average precision (cf. :func:`~sklearn.metrics.average_precision`)
        in scikit-learn is computed without any interpolation. To be consistent
        with this metric, the precision-recall curve is plotted without any
        interpolation as well (step-wise style).

        You can change this style by passing the keyword argument
        `drawstyle="default"`. However, the curve will not be strictly
        consistent with the reported average precision.
        """
        self.ax_, self.figure_, name = self._validate_plot_params(ax=ax, name=name)

        line_kwargs = {"drawstyle": "steps-post"}
        if self.average_precision is not None and name is not None:
            line_kwargs["label"] = f"{name} (AP = {self.average_precision:0.2f})"
        elif self.average_precision is not None:
            line_kwargs["label"] = f"AP = {self.average_precision:0.2f}"
        elif name is not None:
            line_kwargs["label"] = name
        line_kwargs.update(**kwargs)

        (self.line_,) = self.ax_.plot(self.recall, self.precision, **line_kwargs)
        info_pos_label = (
            f" (Positive label: {self.pos_label})" if self.pos_label is not None else ""
        )

        xlabel = "Recall" + info_pos_label
        ylabel = "Precision" + info_pos_label
        self.ax_.set(xlabel=xlabel, ylabel=ylabel)

        if "label" in line_kwargs:
            self.ax_.legend(loc="lower left")

        if plot_uncertainty:
            plot_sampling_uncertainty(
                self.ax_,
                sampling_uncertainty=self.sampling_uncertainty)

        return self

    @classmethod
    def from_estimator(
        cls,
        estimator,
        X,
        y,
        *,
        sample_weight=None,
        pos_label=None,
        drop_intermediate=False,
        response_method="auto",
        name=None,
        ax=None,
        plot_uncertainty=False,
        uncertainty_n_std=3,
        uncertainty_n_bins=500,
        **kwargs,
    ):
        """Plot precision-recall curve given an estimator and some data.

        Parameters
        ----------
        estimator : estimator instance
            Fitted classifier or a fitted :class:`~sklearn.pipeline.Pipeline`
            in which the last estimator is a classifier.

        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Input values.

        y : array-like of shape (n_samples,)
            Target values.

        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights.

        pos_label : str or int, default=None
            The class considered as the positive class when computing the
            precision and recall metrics. By default, `estimators.classes_[1]`
            is considered as the positive class.

        drop_intermediate : bool, default=False
            Whether to drop some suboptimal thresholds which would not appear
            on a plotted precision-recall curve. This is useful in order to
            create lighter precision-recall curves.

            .. versionadded:: 1.3

        response_method : {'predict_proba', 'decision_function', 'auto'}, \
            default='auto'
            Specifies whether to use :term:`predict_proba` or
            :term:`decision_function` as the target response. If set to 'auto',
            :term:`predict_proba` is tried first and if it does not exist
            :term:`decision_function` is tried next.

        name : str, default=None
            Name for labeling curve. If `None`, no name is used.

        ax : matplotlib axes, default=None
            Axes object to plot on. If `None`, a new figure and axes is created.

        plot_uncertainty : bool, default=False
           Plot sampling uncertainty.

            .. versionadded:: 1.2.3

        uncertainty_n_std : int, default=3
           Number of standard deviation to plot for sampling uncertainty level.
           Relevant only if plot_uncertainty = True.
           see more in :meth:`sklearn.metrics._plot.uncertainty.plot_sampling_uncertainty`

            .. versionadded:: 1.2.3

        uncertainty_n_bins : int, default=500
           Number of bins to use for the 2D grid to compute uncertainty for each point.
           Relevant only if plot_uncertainty = True.
           see more in :meth:`sklearn.metrics._plot.uncertainty.compute_sampling_uncertainty`

            .. versionadded:: 1.2.3

        **kwargs : dict
            Keyword arguments to be passed to matplotlib's `plot`.

        Returns
        -------
        display : :class:`~sklearn.metrics.PrecisionRecallDisplay`

        See Also
        --------
        PrecisionRecallDisplay.from_predictions : Plot precision-recall curve
            using estimated probabilities or output of decision function.

        Notes
        -----
        The average precision (cf. :func:`~sklearn.metrics.average_precision`)
        in scikit-learn is computed without any interpolation. To be consistent
        with this metric, the precision-recall curve is plotted without any
        interpolation as well (step-wise style).

        You can change this style by passing the keyword argument
        `drawstyle="default"`. However, the curve will not be strictly
        consistent with the reported average precision.

        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> from sklearn.datasets import make_classification
        >>> from sklearn.metrics import PrecisionRecallDisplay
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn.linear_model import LogisticRegression
        >>> X, y = make_classification(random_state=0)
        >>> X_train, X_test, y_train, y_test = train_test_split(
        ...         X, y, random_state=0)
        >>> clf = LogisticRegression()
        >>> clf.fit(X_train, y_train)
        LogisticRegression()
        >>> PrecisionRecallDisplay.from_estimator(
        ...    clf, X_test, y_test)
        <...>
        >>> plt.show()
        """
        y_pred, pos_label, name = cls._validate_and_get_response_values(
            estimator,
            X,
            y,
            response_method=response_method,
            pos_label=pos_label,
            name=name,
        )

        return cls.from_predictions(
            y,
            y_pred,
            sample_weight=sample_weight,
            name=name,
            pos_label=pos_label,
            drop_intermediate=drop_intermediate,
            ax=ax,
            plot_uncertainty=plot_uncertainty,
            uncertainty_n_std=uncertainty_n_std,
            uncertainty_n_bins=uncertainty_n_bins,
            **kwargs,
        )

    @classmethod
    def from_predictions(
        cls,
        y_true,
        y_pred,
        *,
        sample_weight=None,
        pos_label=None,
        drop_intermediate=False,
        name=None,
        ax=None,
        plot_uncertainty=False,
        uncertainty_n_std=3,
        uncertainty_n_bins=500,
        **kwargs,
    ):
        """Plot precision-recall curve given binary class predictions.

        Parameters
        ----------
        y_true : array-like of shape (n_samples,)
            True binary labels.

        y_pred : array-like of shape (n_samples,)
            Estimated probabilities or output of decision function.

        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights.

        pos_label : str or int, default=None
            The class considered as the positive class when computing the
            precision and recall metrics.

        drop_intermediate : bool, default=False
            Whether to drop some suboptimal thresholds which would not appear
            on a plotted precision-recall curve. This is useful in order to
            create lighter precision-recall curves.

            .. versionadded:: 1.3

        name : str, default=None
            Name for labeling curve. If `None`, name will be set to
            `"Classifier"`.

        ax : matplotlib axes, default=None
            Axes object to plot on. If `None`, a new figure and axes is created.

        plot_uncertainty : bool, default=False
           Plot sampling uncertainty.

            .. versionadded:: 1.2.3

        uncertainty_n_std : int, default=3
           Number of standard deviation to plot for sampling uncertainty level.
           Relevant only if plot_uncertainty = True.
           see more in :meth:`sklearn.metrics._plot.uncertainty.plot_sampling_uncertainty`

            .. versionadded:: 1.2.3

        uncertainty_n_bins : int, default=500
           Number of bins to use for the 2D grid to compute uncertainty for each point.
           Relevant only if plot_uncertainty = True.
           see more in :meth:`sklearn.metrics._plot.uncertainty.compute_sampling_uncertainty`

            .. versionadded:: 1.2.3

        **kwargs : dict
            Keyword arguments to be passed to matplotlib's `plot`.

        Returns
        -------
        display : :class:`~sklearn.metrics.PrecisionRecallDisplay`

        See Also
        --------
        PrecisionRecallDisplay.from_estimator : Plot precision-recall curve
            using an estimator.

        Notes
        -----
        The average precision (cf. :func:`~sklearn.metrics.average_precision`)
        in scikit-learn is computed without any interpolation. To be consistent
        with this metric, the precision-recall curve is plotted without any
        interpolation as well (step-wise style).

        You can change this style by passing the keyword argument
        `drawstyle="default"`. However, the curve will not be strictly
        consistent with the reported average precision.

        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> from sklearn.datasets import make_classification
        >>> from sklearn.metrics import PrecisionRecallDisplay
        >>> from sklearn.model_selection import train_test_split
        >>> from sklearn.linear_model import LogisticRegression
        >>> X, y = make_classification(random_state=0)
        >>> X_train, X_test, y_train, y_test = train_test_split(
        ...         X, y, random_state=0)
        >>> clf = LogisticRegression()
        >>> clf.fit(X_train, y_train)
        LogisticRegression()
        >>> y_pred = clf.predict_proba(X_test)[:, 1]
        >>> PrecisionRecallDisplay.from_predictions(
        ...    y_test, y_pred)
        <...>
        >>> plt.show()
        """
        pos_label, name = cls._validate_from_predictions_params(
            y_true, y_pred, sample_weight=sample_weight, pos_label=pos_label, name=name
        )

        precision, recall, thresholds = precision_recall_curve(
            y_true,
            y_pred,
            pos_label=pos_label,
            sample_weight=sample_weight,
            drop_intermediate=drop_intermediate,
        )
        average_precision = average_precision_score(
            y_true, y_pred, pos_label=pos_label, sample_weight=sample_weight
        )

        if plot_uncertainty:
            print(f"{uncertainty_n_std=}  {uncertainty_n_bins=}")
            sampling_uncertainty = compute_sampling_uncertainty("precision_recall", y_true, y_pred, thresholds, uncertainty_n_std, uncertainty_n_bins)
        else:
            sampling_uncertainty = None

        viz = PrecisionRecallDisplay(
            precision=precision,
            recall=recall,
            average_precision=average_precision,
            estimator_name=name,
            pos_label=pos_label,
            sampling_uncertainty=sampling_uncertainty,
        )

        return viz.plot(ax=ax, name=name, plot_uncertainty=plot_uncertainty, **kwargs)
