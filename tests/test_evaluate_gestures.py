from scripts.evaluate_gestures import compute_confusion_matrix, compute_per_class_metrics


def test_perfect_predictions_give_precision_recall_f1_of_one():
    y_true = ["Thumb_Up", "Thumb_Up", "Victory"]
    y_pred = ["Thumb_Up", "Thumb_Up", "Victory"]
    metrics = compute_per_class_metrics(y_true, y_pred, ["Thumb_Up", "Victory"])
    assert metrics["Thumb_Up"]["precision"] == 1.0
    assert metrics["Thumb_Up"]["recall"] == 1.0
    assert metrics["Thumb_Up"]["f1"] == 1.0
    assert metrics["Thumb_Up"]["support"] == 2


def test_confused_classes_reduce_precision_and_recall():
    # 2 real Thumb_Up, one misclassified as Victory; 1 real Victory, correct.
    y_true = ["Thumb_Up", "Thumb_Up", "Victory"]
    y_pred = ["Thumb_Up", "Victory", "Victory"]
    metrics = compute_per_class_metrics(y_true, y_pred, ["Thumb_Up", "Victory"])

    assert metrics["Thumb_Up"]["precision"] == 1.0  # every predicted Thumb_Up was correct
    assert metrics["Thumb_Up"]["recall"] == 0.5      # only found 1 of the 2 real Thumb_Up
    assert metrics["Victory"]["precision"] == 0.5     # 1 of 2 predicted Victory was actually Victory
    assert metrics["Victory"]["recall"] == 1.0


def test_class_with_no_predictions_or_support_has_zero_metrics_not_crash():
    y_true = ["Thumb_Up"]
    y_pred = ["Thumb_Up"]
    metrics = compute_per_class_metrics(y_true, y_pred, ["Thumb_Up", "Fist"])
    assert metrics["Fist"] == {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0}


def test_confusion_matrix_diagonal_for_perfect_predictions():
    y_true = ["A", "A", "B"]
    y_pred = ["A", "A", "B"]
    matrix = compute_confusion_matrix(y_true, y_pred, ["A", "B"])
    assert matrix == [[2, 0], [0, 1]]


def test_confusion_matrix_off_diagonal_for_misclassification():
    y_true = ["A", "B"]
    y_pred = ["B", "B"]
    matrix = compute_confusion_matrix(y_true, y_pred, ["A", "B"])
    # row A: predicted B once (off-diagonal); row B: predicted B once (diagonal)
    assert matrix == [[0, 1], [0, 1]]
