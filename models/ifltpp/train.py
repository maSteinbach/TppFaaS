import dpp
import numpy as np
import torch
from copy import deepcopy
from log import logger
from time import process_time
#torch.set_default_tensor_type(torch.cuda.FloatTensor)

def train_dataset(
    dataset_path: str,
    num_mix_components: int,
    coldstart_feature: bool,
    regularization: int,        # L2 regularization parameter
    max_epochs: int,            # For how many epochs to train
    patience: int,              # After how many consecutive epochs without improvement of val loss to stop training
    mae_loss: bool, 
    seed: int = None
) -> dict:

    logger.info(
        f"Start training ...\n"
        f"- dataset_path: {dataset_path}\n"
        f"- num_mix_components: {num_mix_components}\n"
        f"- coldstart_feature: {coldstart_feature}\n"
        f"- regularization: {regularization}\n"
        f"- max_epochs: {max_epochs}\n"
        f"- patience: {patience}\n"
        f"- mae_loss: {mae_loss}\n"
        f"- seed: {seed}"
    )

    # Config
    if seed is not None:    
        np.random.seed(seed)
        torch.manual_seed(seed)

    # Model config
    context_size = 64               # Size of the RNN hidden vector
    mark_embedding_size = 32        # Size of the mark embedding (used as RNN input)
    coldstart_embedding_size = 32   # Size of the embedding of the coldstart feature (used as RNN input)
    rnn_type = "GRU"                # What RNN to use as an encoder {"RNN", "GRU", "LSTM"}

    # Training config
    batch_size = 64        # Number of sequences in a batch
    learning_rate = 1e-3   # Learning rate for Adam optimizer
    display_step = 50      # Display training statistics after every display_step

    # Load the data
    dataset = dpp.data.load_dataset(dataset_path)
    d_train, d_val, d_test = dataset.train_val_test_split(seed=seed)

    dl_train = d_train.get_dataloader(batch_size=batch_size, shuffle=True)
    dl_val = d_val.get_dataloader(batch_size=batch_size, shuffle=False)
    dl_test = d_test.get_dataloader(batch_size=batch_size, shuffle=False)

    # Define the model
    mean_log_inter_time, std_log_inter_time = d_train.get_inter_time_statistics()

    model = dpp.models.LogNormMix(
        num_marks=d_train.num_marks,
        mean_log_inter_time=mean_log_inter_time,
        std_log_inter_time=std_log_inter_time,
        context_size=context_size,
        mark_embedding_size=mark_embedding_size,
        rnn_type=rnn_type,
        num_mix_components=num_mix_components,
        coldstart_feature=coldstart_feature,
        coldstart_embedding_size=coldstart_embedding_size
    )
    opt = torch.optim.Adam(model.parameters(), weight_decay=regularization, lr=learning_rate)

    # Training
    def inter_time_errors(batch):
        predicted_inter_times, _ = model.predict(batch)
        errors = predicted_inter_times - batch.inter_times
        #indices = torch.nonzero(batch.mask, as_tuple=True)
        #return errors[indices]
        index = torch.nonzero(batch.mask.sum(dim=0), as_tuple=True)[0]  # Only works if all sequences have the same length.
        return errors.index_select(dim=1, index=index)

    def correct_predicted_marks(batch):
        _, predicted_marks = model.predict(batch)
        correct_predictions = predicted_marks == batch.marks
        index = torch.nonzero(batch.mask.sum(dim=0), as_tuple=True)[0]  # Only works if all sequences have the same length.
        return correct_predictions.index_select(dim=1, index=index)
    
    def aggregate_loss_over_dataloader(dl, mae_loss):
        total_loss = 0.0
        total_count = 0
        with torch.no_grad():
            for batch in dl:
                if mae_loss:
                    total_loss += (inter_time_errors(batch).abs().sum() - model.mark_log_prob(batch).sum()).item()
                else:
                    total_loss += -model.log_prob(batch).sum().item()
                total_count += batch.mask.sum().item()
        return total_loss / total_count
    
    def aggregate_mark_nll_over_dataloader(dl):
        total_loss = 0.0
        total_count = 0
        with torch.no_grad():
            for batch in dl:
                total_loss += -model.mark_log_prob(batch).sum().item()
                total_count += batch.mask.sum().item()
        return total_loss / total_count

    def aggregate_mae_over_dataloader(dl):
        total_mae = 0.0
        total_count = 0
        with torch.no_grad():
            for batch in dl:
                total_mae += inter_time_errors(batch).abs().sum().item()
                total_count += batch.mask.sum().item()
        return total_mae / total_count

    def aggregate_accuracy_over_dataloader(dl):
        total_correct_predictions = 0.0
        total_count = 0
        with torch.no_grad():
            for batch in dl:
                total_correct_predictions += correct_predicted_marks(batch).sum().item()
                total_count += batch.mask.sum().item()
        return total_correct_predictions / total_count

    def inter_time_errors_over_dataloader(dl):
        result = torch.Tensor()
        with torch.no_grad():
            for batch in dl:
                result = torch.cat([result, inter_time_errors(batch)], dim=0)
        return result
    
    def correct_predicted_marks_over_dataloader(dl):
        result = torch.Tensor()
        with torch.no_grad():
            for batch in dl:
                result = torch.cat([result, correct_predicted_marks(batch)], dim=0)
        return result

    impatient = 0
    best_loss = np.inf
    best_mae = np.inf
    best_model = deepcopy(model.state_dict())
    start_processtime = process_time()

    for epoch in range(max_epochs):
        model.train()
        for batch in dl_train:
            opt.zero_grad()
            loss = 0.0
            if mae_loss:
                loss = inter_time_errors(batch).abs().mean() - model.mark_log_prob(batch).mean()
            else:
                loss = -model.log_prob(batch).mean()
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            loss_val = aggregate_loss_over_dataloader(dl_val, mae_loss)
            mark_nll_val = aggregate_mark_nll_over_dataloader(dl_val)
            mae_val = aggregate_mae_over_dataloader(dl_val)
            acc_val = aggregate_accuracy_over_dataloader(dl_val)

        if (best_loss - loss_val) < 1e-4:
            impatient += 1
            if loss_val < best_loss:
                best_loss = loss_val
                best_model = deepcopy(model.state_dict())
        else:
            best_loss = loss_val
            best_model = deepcopy(model.state_dict())
            impatient = 0

        if impatient >= patience:
            logger.info(f'Breaking due to early stopping at epoch {epoch}')
            break

        if epoch % display_step == 0:
            logger.info(f"Epoch {epoch:4d} of {max_epochs:4d}: loss_train_last_batch = {loss.item():.3f}, loss_val = {loss_val:.3f}, mark_nll_val = {mark_nll_val:.3f}, mae_val = {mae_val:.3f}, acc_val = {acc_val:.3f}")

    trained_processtime = process_time() - start_processtime
    logger.info(f"Trained process time: {trained_processtime:.3f}s\n"
                f"Trained epochs: {epoch+1}")

    # Evaluation
    results = {}
    results["trained_processtime"] = trained_processtime
    results["trained_epochs"] = epoch + 1
    model.load_state_dict(best_model)
    model.eval()
    # Evaluation via total loss
    with torch.no_grad():
        final_loss_train = aggregate_loss_over_dataloader(dl_train, mae_loss)
        final_loss_val = aggregate_loss_over_dataloader(dl_val, mae_loss)
        final_loss_test = aggregate_loss_over_dataloader(dl_test, mae_loss)
    results["final_loss_train"] = final_loss_train
    results["final_loss_val"] = final_loss_val
    results["final_loss_test"] = final_loss_test
    logger.info(f'Total loss:\n'
        f'- Train: {final_loss_train:.3f}\n'
        f'- Val:   {final_loss_val:.3f}\n'
        f'- Test:  {final_loss_test:.3f}')
    # Evaluation via mark negative log-likelihood
    with torch.no_grad():
        final_mark_nll_train = aggregate_mark_nll_over_dataloader(dl_train)
        final_mark_nll_val = aggregate_mark_nll_over_dataloader(dl_val)
        final_mark_nll_test = aggregate_mark_nll_over_dataloader(dl_test)
    results["final_mark_nll_train"] = final_mark_nll_train
    results["final_mark_nll_val"] = final_mark_nll_val
    results["final_mark_nll_test"] = final_mark_nll_test
    logger.info(f'Mark negative log-likelihood:\n'
        f'- Train: {final_mark_nll_train:.3f}\n'
        f'- Val:   {final_mark_nll_val:.3f}\n'
        f'- Test:  {final_mark_nll_test:.3f}')
    # Evaluation via accuracy
    with torch.no_grad():
        final_acc_train = aggregate_accuracy_over_dataloader(dl_train)
        final_acc_val = aggregate_accuracy_over_dataloader(dl_val)
        final_acc_test = aggregate_accuracy_over_dataloader(dl_test)
    results["final_acc_train"] = final_acc_train
    results["final_acc_val"] = final_acc_val
    results["final_acc_test"] = final_acc_test
    logger.info(f'Accuracy:\n'
        f'- Train: {final_acc_train:.3f}\n'
        f'- Val:   {final_acc_val:.3f}\n'
        f'- Test:  {final_acc_test:.3f}')
    results["correct_predicted_marks"] = correct_predicted_marks_over_dataloader(dl_test).cpu().numpy()
    if mae_loss:
        # Evaluation via mean absolute error
        with torch.no_grad():
            final_mae_train = aggregate_mae_over_dataloader(dl_train)
            final_mae_val = aggregate_mae_over_dataloader(dl_val)
            final_mae_test = aggregate_mae_over_dataloader(dl_test)
        results["final_mae_train"] = final_mae_train
        results["final_mae_val"] = final_mae_val
        results["final_mae_test"] = final_mae_test
        logger.info(f'Mean absolute error:\n'
            f'- Train: {final_mae_train:.3f}\n'
            f'- Val:   {final_mae_val:.3f}\n'
            f'- Test:  {final_mae_test:.3f}')
        results["inter_time_errors"] = inter_time_errors_over_dataloader(dl_test).cpu().numpy()

    return results