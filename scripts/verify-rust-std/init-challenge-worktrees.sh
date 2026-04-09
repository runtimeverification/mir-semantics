#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 4 ]]; then
    echo "usage: $0 <repo-root> <portfolio-worktree> <challenge-ref-root> <worktree-root>" >&2
    exit 2
fi

repo_root=$1
portfolio_root=$2
challenge_ref_root=$3
worktree_root=$4

manifest_path="$portfolio_root/docs/verify-rust-std/portfolio/manifest.tsv"
issue_state_json="$portfolio_root/docs/verify-rust-std/portfolio/issue-states.json"

mkdir -p "$worktree_root"
mkdir -p "$(dirname "$manifest_path")"

gh issue list -R model-checking/verify-rust-std --label Challenge --state all --limit 200 \
    --json number,state,title,url >"$issue_state_json"

issue_state_for() {
    local issue_number=$1
    jq -r --arg n "$issue_number" '.[] | select((.number | tostring) == $n) | .state' "$issue_state_json"
}

render_template() {
    local template=$1
    local out=$2
    local challenge_id=$3
    local slug=$4
    local title=$5
    local doc_url=$6
    local tracking_url=$7
    local tracking_state=$8
    local branch_name=$9
    local worktree_path=${10}
    local challenge_doc_dir=${11}
    local challenge_artifact_dir=${12}

    sed \
        -e "s|{{CHALLENGE_ID}}|$challenge_id|g" \
        -e "s|{{CHALLENGE_SLUG}}|$slug|g" \
        -e "s|{{CHALLENGE_TITLE}}|$title|g" \
        -e "s|{{CHALLENGE_DOC_URL}}|$doc_url|g" \
        -e "s|{{TRACKING_ISSUE_URL}}|$tracking_url|g" \
        -e "s|{{TRACKING_ISSUE_STATE}}|$tracking_state|g" \
        -e "s|{{BRANCH_NAME}}|$branch_name|g" \
        -e "s|{{WORKTREE_PATH}}|$worktree_path|g" \
        -e "s|{{CHALLENGE_DOC_DIR}}|$challenge_doc_dir|g" \
        -e "s|{{CHALLENGE_ARTIFACT_DIR}}|$challenge_artifact_dir|g" \
        "$template" >"$out"
}

printf "challenge_id\tslug\tissue_state\tbranch\tworktree\ttracking_issue\tchallenge_page\tplanner_doc\tgenerator_doc\tevaluator_doc\trubric_doc\tpr_url\n" >"$manifest_path"

for challenge_file in "$challenge_ref_root"/doc/src/challenges/*.md; do
    challenge_base=$(basename "$challenge_file")
    challenge_id=${challenge_base%%-*}
    slug=${challenge_base#"$challenge_id"-}
    slug=${slug%.md}
    title=$(sed -n '1s/^# //p' "$challenge_file" | sed 's/\[\^challenge_id\].*//')
    tracking_url=$(sed -n '1,12p' "$challenge_file" | sed -n 's/^- \*\*Tracking Issue:\*\* \(.*\)$/\1/p')
    issue_number=$(printf '%s' "$tracking_url" | sed -n 's|.*issues/\([0-9][0-9]*\).*|\1|p')
    issue_state=$(issue_state_for "$issue_number")
    if [[ -z "$issue_state" ]]; then
        issue_state="UNKNOWN"
    fi
    doc_url="https://github.com/model-checking/verify-rust-std/blob/main/doc/src/challenges/${challenge_base}"
    branch="verify-rust-std/reexec-${challenge_id}-${slug}"
    worktree="$worktree_root/${challenge_id}-${slug}"
    challenge_doc_dir="docs/verify-rust-std/challenges/${challenge_id}-${slug}"
    challenge_artifact_dir="kmir/src/tests/integration/data/verify-rust-std/${challenge_id}-${slug}"

    if [[ ! -d "$worktree/.git" ]]; then
        git -C "$repo_root" worktree add -b "$branch" "$worktree" origin/master
    fi

    mkdir -p "$worktree/$challenge_doc_dir"
    mkdir -p "$worktree/$challenge_artifact_dir"
    cp "$portfolio_root/docs/verify-rust-std/portfolio/rubric.md" "$worktree/$challenge_doc_dir/rubric.md"

    render_template "$portfolio_root/docs/verify-rust-std/templates/challenge-README.md.in" \
        "$worktree/$challenge_artifact_dir/README.md" \
        "$challenge_id" "$slug" "$title" "$doc_url" "$tracking_url" "$issue_state" \
        "$branch" "$worktree" "$challenge_doc_dir" "$challenge_artifact_dir"
    render_template "$portfolio_root/docs/verify-rust-std/templates/planner.md.in" \
        "$worktree/$challenge_doc_dir/planner.md" \
        "$challenge_id" "$slug" "$title" "$doc_url" "$tracking_url" "$issue_state" \
        "$branch" "$worktree" "$challenge_doc_dir" "$challenge_artifact_dir"
    render_template "$portfolio_root/docs/verify-rust-std/templates/generator.md.in" \
        "$worktree/$challenge_doc_dir/generator.md" \
        "$challenge_id" "$slug" "$title" "$doc_url" "$tracking_url" "$issue_state" \
        "$branch" "$worktree" "$challenge_doc_dir" "$challenge_artifact_dir"
    render_template "$portfolio_root/docs/verify-rust-std/templates/evaluator.md.in" \
        "$worktree/$challenge_doc_dir/evaluator.md" \
        "$challenge_id" "$slug" "$title" "$doc_url" "$tracking_url" "$issue_state" \
        "$branch" "$worktree" "$challenge_doc_dir" "$challenge_artifact_dir"

    if ! git -C "$worktree" diff --quiet -- "$challenge_doc_dir" "$challenge_artifact_dir"; then
        git -C "$worktree" add "$challenge_doc_dir" "$challenge_artifact_dir"
        git -C "$worktree" commit -m "chore(verify-rust-std): initialize challenge ${challenge_id} orchestration docs"
    fi

    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\n" \
        "$challenge_id" "$slug" "$issue_state" "$branch" "$worktree" "$tracking_url" "$doc_url" \
        "$challenge_doc_dir/planner.md" "$challenge_doc_dir/generator.md" \
        "$challenge_doc_dir/evaluator.md" "$challenge_doc_dir/rubric.md" >>"$manifest_path"
done
