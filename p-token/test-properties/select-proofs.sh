# /bin/bash
#
# Usage: ./select-proofs.sh "Table Header"
#  - select the proofs from one of the tables in the file
#    (the first match will be taken)
##########################################################

USAGE=$(head -6 $0)

if [ -z "$1" ]; then
    head -6 $0
    exit 1
fi

HEADING="$1"

if ! (grep -e "^| $HEADING" $0 > /dev/null); then
    echo "[ERROR] '| $HEADING..': not a table header. Must provide a table heading to select proofs."
    exit 1
fi

sed -n -e "/^| ${HEADING}.*/,/^\$/ {/| ${HEADING}.*/d; /^\$/q; s/^| \(test_p[a-zA-Z0-9_]*\) .*/\1/p}" <<EOF

| Passing                                       |
|-----------------------------------------------|
| test_ptoken_domain_data                       |
| test_process_burn                             |
| test_process_approve_checked                  |
| test_process_withdraw_excess_lamports_account |
| test_process_transfer                         |
| test_process_mint_to                          |
| test_process_approve                          |
| test_process_close_account                    |
| test_process_sync_native                      |
| test_process_burn_checked                     |
| test_process_revoke                           |
| test_process_freeze_account                   |
| test_process_thaw_account                     |
| test_process_mint_to_checked                  |
| test_process_transfer_checked                 |
| test_process_get_account_data_size            |
| test_process_initialize_immutable_owner       |
| test_process_set_authority_account            |

| Failing nodes                           |
|-----------------------------------------|
| test_process_initialize_account         |
| test_process_initialize_account2        |
| test_process_initialize_account3        |
| test_process_initialize_mint_freeze     |
| test_process_initialize_mint2_freeze    |
| test_process_initialize_mint_no_freeze  |
| test_process_initialize_mint2_no_freeze |

| Other issues                     |
|----------------------------------|
| test_process_amount_to_ui_amount |
| test_process_ui_amount_to_amount |

| Performance issues                         |
|--------------------------------------------|
| test_process_withdraw_excess_lamports_mint |
| test_process_set_authority_mint            |


| Missing Multisig cheat code                             |
|---------------------------------------------------------|
| test_process_withdraw_excess_lamports_multisig          |
| test_process_approve_multisig                           |
| test_process_approve_checked_multisig                   |
| test_process_withdraw_excess_lamports_account_multisig  |
| test_process_withdraw_excess_lamports_mint_multisig     |
| test_process_withdraw_excess_lamports_multisig_multisig |
| test_process_transfer_multisig                          |
| test_process_mint_to_multisig                           |
| test_process_burn_multisig                              |
| test_process_close_account_multisig                     |
| test_process_transfer_checked_multisig                  |
| test_process_burn_checked_multisig                      |
| test_process_revoke_multisig                            |
| test_process_freeze_account_multisig                    |
| test_process_thaw_account_multisig                      |
| test_process_mint_to_checked_multisig                   |
| test_process_set_authority_account_multisig             |
| test_process_set_authority_mint_multisig                |
| test_process_initialize_multisig                        |
| test_process_initialize_multisig2                       |

EOF
