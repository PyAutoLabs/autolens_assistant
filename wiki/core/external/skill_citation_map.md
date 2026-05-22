---
title: Skill external-citation map
type: external_index
audience: all
---

# Skill → external resource map

**This table is load-bearing.** Each `al_*` skill's `## Further reading` section is
generated from the matching row. One line per skill, three audience-tagged links.

When a new `al_*` skill is added, append a row here, then run the per-skill
`## Further reading` edit (see `skills/_style.md` "External resource citation").

## URL expansion

Cells reference the path relative to each resource. Expand using:

- **HowToLens (notebook):** `https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/<cell>.ipynb`
- **HowToLens (script):** `https://github.com/PyAutoLabs/HowToLens/blob/main/scripts/<cell>.py`
- **RTD:** `https://pyautolens.readthedocs.io/en/latest/<cell>.html`
- **workspace/lens script:** `https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/<cell>`

Pick notebook vs script per audience (default `.ipynb` for student-leaning users;
`.py` for returning PyAutoLens users).

## Table

| Skill | HowToLens (student) | RTD (general) | workspace/lens (experienced) |
|-------|---------------------|---------------|-------------------------------|
| al_setup_environment | _ | installation/overview | _ |
| al_prepare_imaging_data | chapter_1_introduction/tutorial_6_data | overview/overview_2_new_user_guide | imaging/data_preparation/start_here.py |
| al_simulate_dataset | chapter_1_introduction/tutorial_3_more_ray_tracing | overview/overview_1_start_here | imaging/simulators/start_here.py |
| al_build_imaging_model | chapter_2_lens_modeling/tutorial_1_non_linear_search | general/model_cookbook | imaging/modeling/start_here.py |
| al_build_interferometer_model | _ | overview/overview_3_features | interferometer/start_here.py |
| al_custom_profile | chapter_1_introduction/tutorial_1_grids_and_galaxies | general/model_cookbook | guides/profiles/light.py |
| al_configure_search | chapter_optional/tutorial_searches | overview/overview_3_features | guides/modeling/slam_start_here.py |
| al_run_search | chapter_2_lens_modeling/tutorial_2_practicalities | overview/overview_2_new_user_guide | imaging/start_here.py |
| al_chain_searches | chapter_3_search_chaining/tutorial_1_search_chaining | general/model_cookbook | guides/modeling/slam_start_here.py |
| al_run_slam_pipeline | chapter_3_search_chaining/tutorial_6_slam | overview/overview_3_features | guides/modeling/slam_start_here.py |
| al_debug_fit_failure | chapter_2_lens_modeling/tutorial_4_dealing_with_failure | general/demagnified_solutions | guides/tracer.py |
| al_load_results | chapter_2_lens_modeling/tutorial_7_results | general/likelihood_function | guides/results/start_here.py |
| al_plot_tracer | chapter_1_introduction/tutorial_2_ray_tracing | overview/overview_1_start_here | guides/tracer.py |
| al_plot_fit_residuals | chapter_1_introduction/tutorial_7_fitting | general/likelihood_function | imaging/results/start_here.py |
| al_inspect_source_reconstruction | chapter_4_pixelizations/tutorial_3_inversions | overview/overview_3_features | imaging/features/pixelization/modeling.py |
| al_update_wiki | _ | _ | _ |
| al_audit_skill_apis | _ | _ | _ |
| al_ingest_paper | _ | _ | _ |
| al_point_source | chapter_2_lens_modeling/tutorial_3_positions | overview/overview_3_features | point_source/start_here.py |
| al_time_delay_cosmography | _ | overview/overview_3_features | point_source/features/time_delays.py |
| al_subhalo_detect | chapter_4_pixelizations/tutorial_3_inversions | overview/overview_3_features | imaging/features/advanced/subhalo/detect/start_here.py |
| al_sensitivity_mapping | _ | overview/overview_3_features | imaging/features/advanced/subhalo/sensitivity/start_here.py |
| al_group_lensing | _ | overview/overview_3_features | group/start_here.py |
| al_cluster_csv_api | _ | overview/overview_3_features | cluster/csv_api.py |
| al_multi_dataset | _ | overview/overview_3_features | multi/start_here.py |
| al_weak_lensing | _ | overview/overview_3_features | weak/fit.py |
| al_hierarchical_inference | _ | overview/overview_3_features | guides/modeling/advanced/hierarchical.py |
| al_aggregator_bulk_analysis | _ | overview/overview_3_features | guides/results/start_here.py |
| al_adaptive_pixelization | chapter_4_pixelizations/tutorial_5_adaptive_pixelization | overview/overview_3_features | imaging/features/pixelization/adaptive.py |
| al_mge_decomposition | _ | overview/overview_3_features | imaging/features/multi_gaussian_expansion/modeling.py |
| al_datacube_modeling | _ | overview/overview_3_features | interferometer/features/datacube/start_here.py |
| al_custom_analysis | _ | overview/overview_3_features | guides/advanced/custom_analysis.py |

Cells set to `_` mean the resource has no direct match for this skill (omit the
bullet in the skill's `## Further reading` block, keep the others).

## Template for the inserted skill block

Every skill's `## Further reading` block follows this template:

```markdown
## Further reading

- **Student / new to lensing** — [HowToLens: <tutorial title>](<URL>): one-line
  hook on what the tutorial teaches.
- **General reference** — [RTD: <page title>](<URL>): the canonical PyAutoLens
  documentation page covering this feature.
- **Experienced PyAutoLens user** — [workspace/lens: <script name>](<URL>): a
  production-style example to fork from.
```

If a row's cell is `_`, omit that bullet but keep the others. If all three cells
are `_` (e.g. `al_update_wiki`), omit the `## Further reading` block entirely —
the skill is internal to the workspace itself.
