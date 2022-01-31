import dpp
import pickle
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from log import logger
from statistics import mean
from train import train_dataset
from typing import List

@dataclass
class ResultItem:
    dataset_name: str
    num_mix_components: int
    mae_loss: bool
    cold_starts: bool
    regularization: float
    max_epochs: int
    patience: int
    seed: int
    trained_processtime: List[float] = field(default_factory=list)
    trained_epochs: List[float] = field(default_factory=list)
    final_loss_val: List[float] = field(default_factory=list)
    final_loss_test: List[float] = field(default_factory=list)
    final_time_nll_test: List[float] = field(default_factory=list)
    final_mark_nll_test: List[float] = field(default_factory=list)
    final_acc_test: List[float] = field(default_factory=list)
    correct_predicted_marks: list = field(default_factory=list)
    final_mae_test: List[float] = field(default_factory=list)
    inter_time_errors: list = field(default_factory=list)

    def loss_val_mean(self) -> float:
        return mean(self.final_loss_val)

def feature_combinations(filename: str) -> List[tuple]:
    if "_b_" in filename:
        return [False, True] # High load dataset.
    else:
        return [False] # Low load dataset.

def train_all(
    directory: str,
    regularizations: List[float],
    iterations: int,
    max_epochs_nll: int,
    max_epochs_mae: int,
    patience_nll: int,
    patience_mae: int,
    num_mix_components: int = 64,
    seed: int = None
) -> None:
    filenames = dpp.data.list_datasets(f"../../data/{directory}")
    logger.info(f"Training of files: {filenames}")
    for i, name in enumerate(filenames):
        logger.info(f"=== Start training file {i+1} of {len(filenames)}: {name} ===")
        results = []
        for cold_starts in feature_combinations(name):
            for mae_loss in [False, True]:
                # Train with different regularization settings. But keep only one.
                items = []
                for j, reg in enumerate(regularizations):
                    max_epochs = None
                    patience = None
                    if mae_loss: 
                        max_epochs = max_epochs_mae
                        patience = patience_mae
                    else: 
                        max_epochs = max_epochs_nll
                        patience = patience_nll
                    result_item = ResultItem(
                        dataset_name=name,
                        num_mix_components=num_mix_components,
                        mae_loss=mae_loss,
                        cold_starts=cold_starts,
                        regularization=reg,
                        max_epochs=max_epochs,
                        patience=patience,
                        seed=seed
                    )
                    for k in range(iterations):
                        logger.info(f"=== Iteration {k+1} of {iterations} ===")
                        iteration_result = train_dataset(
                            dataset_path=f"{directory}/{name}",
                            num_mix_components=num_mix_components,
                            coldstart_feature=cold_starts,
                            mae_loss=mae_loss,
                            regularization=reg,
                            max_epochs=max_epochs,
                            patience=patience,
                            seed=seed
                        )
                        result_item.trained_processtime.append(iteration_result.get("trained_processtime"))
                        result_item.trained_epochs.append(iteration_result.get("trained_epochs"))
                        result_item.final_loss_val.append(iteration_result.get("final_loss_val"))
                        result_item.final_loss_test.append(iteration_result.get("final_loss_test"))
                        result_item.final_time_nll_test.append(iteration_result.get("final_loss_test") - iteration_result.get("final_mark_nll_test"))
                        result_item.final_mark_nll_test.append(iteration_result.get("final_mark_nll_test"))
                        result_item.final_acc_test.append(iteration_result.get("final_acc_test"))
                        result_item.correct_predicted_marks.append(iteration_result.get("correct_predicted_marks"))
                        assert type(result_item.trained_processtime[k]) == float
                        assert type(result_item.trained_epochs[k]) == int
                        assert type(result_item.final_loss_val[k]) == float
                        assert type(result_item.final_loss_test[k]) == float
                        assert type(result_item.final_time_nll_test[k]) == float
                        assert type(result_item.final_mark_nll_test[k]) == float
                        assert type(result_item.final_acc_test[k]) == float
                        assert result_item.correct_predicted_marks[k].shape[0] > 0
                        assert result_item.correct_predicted_marks[k].shape[1] > 0
                        assert (k+1) == len(result_item.final_loss_val) == len(result_item.final_loss_test) == len(result_item.final_time_nll_test) == len(result_item.final_mark_nll_test) == len(result_item.final_acc_test) == len(result_item.correct_predicted_marks) == len(result_item.trained_processtime) == len(result_item.trained_epochs)
                        if mae_loss:
                            result_item.final_mae_test.append(iteration_result.get("final_mae_test"))
                            result_item.inter_time_errors.append(iteration_result.get("inter_time_errors"))
                            assert type(result_item.final_mae_test[k]) == float
                            assert result_item.inter_time_errors[k].shape[0] > 0
                            assert result_item.inter_time_errors[k].shape[1] > 0
                            assert (k+1) == len(result_item.final_mae_test) == len(result_item.inter_time_errors)
                    logger.info(f"Average validation loss: {result_item.loss_val_mean():.3f}")
                    items.append(result_item)
                    assert len(items) == (j+1)
                # Keep only the item with the best average validation loss value.
                best_loss = items[0].loss_val_mean()
                best_idx = 0
                for idx, item in enumerate(items):
                    new_loss = item.loss_val_mean()
                    if new_loss < best_loss:
                        best_loss = new_loss
                        best_idx = idx
                logger.info(f"Best average validation loss of {items[best_idx].loss_val_mean():.3f}"
                            f" achieved with regularization {items[best_idx].regularization}")                
                results.append(items[best_idx])

        assert len(results) == (2*len(feature_combinations(name)))

        datetimestr = datetime.now().strftime("%Y%m%d_%H:%M")
        with open(
            f"../../evaluation/train_results/{directory}/"
            f"{datetimestr}_file_{name}_iter_{iterations}_maxepochsnll_{max_epochs_nll}_maxepochsmae_{max_epochs_mae}_"
            f"patiencenll_{patience_nll}_patiencemae_{patience_mae}.pkl", "wb"
        ) as f:
            pickle.dump(results, f)
    logger.info("=== FINISHED TRAINING ===")

if __name__=='__main__':
    # Configuration
    iterations = 10
    directory = "final_low_load_n_1000"
    #directory = "final_high_load_n_1000"
    #regularizations = [0.0, 1e-3, 1e-5]
    #regularizations = [1e-3, 1e-5]
    regularizations = [1e-5]
    max_epochs_nll = 2000
    max_epochs_mae = 4000
    patience_nll = 100
    patience_mae = 200
    num_mix_components = 64
    seed = None
    
    train_all(
        directory=directory,
        regularizations=regularizations,
        iterations=iterations,
        max_epochs_nll=max_epochs_nll,
        max_epochs_mae=max_epochs_mae,
        patience_nll=patience_nll,
        patience_mae=patience_mae,
        num_mix_components=num_mix_components,
        seed=seed
    )