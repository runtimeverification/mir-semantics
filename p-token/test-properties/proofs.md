Proofs to run with `run-proofs.sh -a`:

| Start symbol name                             |
|-----------------------------------------------|
| test_ptoken_domain_data                       |
| test_process_approve                          |
| test_process_approve_checked                  |
| test_process_withdraw_excess_lamports_account |
| test_process_withdraw_excess_lamports_mint    |
| test_process_initialize_mint_freeze           |
| test_process_initialize_mint_no_freeze        |
| test_process_initialize_account               |
| test_process_initialize_account2              |
| test_process_transfer                         |
| test_process_mint_to                          |
| test_process_burn                             |
| test_process_close_account                    |
| test_process_transfer_checked                 |
| test_process_burn_checked                     |
| test_process_initialize_account3              |
| test_process_initialize_mint2_freeze          |
| test_process_initialize_mint2_no_freeze       |
| test_process_revoke                           |
| test_process_freeze_account                   |
| test_process_thaw_account                     |
| test_process_mint_to_checked                  |
| test_process_sync_native                      |
| test_process_get_account_data_size            |
| test_process_initialize_immutable_owner       |
| test_process_amount_to_ui_amount              |
| test_process_ui_amount_to_amount              |
| test_process_set_authority_account            |
| test_process_set_authority_mint               |

Cheat codes are missing or a problem for these proofs, therefore not recommended to execute them
(keep the empty first column so `run-proofs.sh` won't pick these up):

|   | test_process_initialize_multisig  |
|   | test_process_initialize_multisig2 |
