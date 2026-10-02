---
id: forward_model_consistency
version: 1
kind: oneshot
prompt_sha256: 59eaa5f85976add1a52a7aebe92108499144b0e1a4a1c93fe7f42e5b6a79c694
budget:
  compute_seconds: 120
  run_seconds: 300
datasets:
  - dataset/interferometer/forward_model_consistency
workspace_packages:
  - imaging
  - point_source
  - interferometer
added: 2026-10-02
---

# Forward-model consistency

## Prompt

```text
I am a researcher who wants the code and a finished simulation, without fitting. Build one quadruply imaged lens and produce mutually consistent imaging, point-source and interferometer datasets.

Use Planck15 cosmology, lens redshift 0.5 and source redshift 1.0. The lens is centred at (0,0), a circular EPL with Einstein radius 1.0 arcsec and three-dimensional density slope 2.2, plus external shear of magnitude 0.15 at 23 degrees counter-clockwise from +x. There is no lens light. The source is a circular Sersic with total unlensed AB magnitude 23.0 at detector zero point 25.0 (total counts/s = 10^[-0.4(m-ZP)]), effective radius 0.035 arcsec and index 1.0. Choose its (y,x) centre inside the tangential caustic so there are four images; you may choose any centre with both absolute coordinates at most 0.08 arcsec. Report intensity in counts/s/pixel at the effective radius (include pixel area in the integrated-flux conversion), and EPL convergence normalization K in kappa(r)=K*r^(1-slope).

Use a 64x64 grid with 0.08 arcsec pixels, uniform over-sampling 4, a normalized 11x11 Gaussian PSF with FWHM 0.12 arcsec, exposure 10000 seconds, sky 0.01 counts/s/pixel, Poisson image noise and seed 1729. Subtract the mean sky. Write image.fits, noise_map.fits and psf.fits using the library FITS conventions. Solve the source-centre positions to 0.0005 arcsec with magnification threshold 0.01. Save a library PointDataset with positions, absolute magnifications as unit-source fluxes, and time delays in days relative to the earliest arrival (position uncertainty 0.001 arcsec; flux and delay uncertainty 0.01). Also report signed magnifications. Save the Tracer for read-back.

Simulate the same tracer with the supplied dataset/interferometer/forward_model_consistency/uv_wavelengths.fits, exact DFT, the same sky grid/over-sampling/exposure, Gaussian visibility noise sigma 0.001 and seed 1729. Write visibilities.fits, visibility_noise.fits and uv_wavelengths.fits, plus dirty_image.fits from the dataset's inverse transform. Derive a boolean imaging mask from the solved positions using the data-preparation tools: all four image pixels included, lens-centre pixels excluded (True means excluded). Write mask.fits. Make a real PNG showing imaging with solved positions and critical curves overlaid, and the dirty image beside it. Check local maxima near the positions in both images, explaining any discrepancy.

Write all delivered files inside artifacts/ in the result directory named by the final instruction below, so they survive cleanup. In result.json use paths relative to that result directory and exactly these top-level keys: source_centre (two floats, y then x); conversions (object with epl_normalization, intensity, psf_sigma_pixels, gamma_1, gamma_2); positions (list of [y,x]); magnifications (signed floats, same order); time_delays_days (floats, same order, earliest is zero); files (object with keys image, noise_map, psf, point, tracer, visibilities, visibility_noise, uv_wavelengths, dirty_image, mask, figure); summary (brief string). Derive the numbers from the saved products, not from the request. Finish in five minutes and keep interpreter time below two minutes; no inference is needed.
```

## What this measures

Physical-to-library conversions and agreement between independently computed
imaging, point-source and visibility products. The circular EPL is deliberately
unambiguous about Einstein-radius conventions; rotated shear breaks y/x symmetry.
Source centre is a permitted choice: the hidden scorer regenerates references for
the submitted centre, rather than requiring an undisclosed centre.

## Score

All harness gates apply. `library_readers` requires Imaging.from_fits,
Interferometer.from_fits, Mask2D.from_fits and library JSON round-trips for Tracer
and PointDataset, plus a readable dirty image. Invalid or escaped artifact paths
fail. Stored FITS and JSON are retained under the run directory for rescoring.

Metrics are clipped to [0,1]. A normalized max-absolute array error E maps to
max(0,1-E/tolerance); normalization is max(abs(reference)), floored at 1e-12.
Image/noise/PSF tolerate 0.02; visibilities and dirty image 0.02. Conversions
and saved-model parameters tolerate 0.01. Positions use optimal Euclidean pairing
and max error / one pixel; magnifications tolerate 0.05 and delays 0.02 (delays
normalized by the full delay span, preserving the zero arrival). Multiplicity is
binary ==4, and report arrays must agree with their persisted point dataset.

Each cross-package row is the fraction of submitted positions within 1.5 pixels
of a positive local maximum above 5% of the global peak. Both imaging and dirty
rows are emitted twice (`*_weight_2`) to give exactly twice the contribution in
the existing unweighted harness, without changing any other card. A swapped y/x
set must fail both rows in the reference fixture. The mask row is binary; the
figure row requires a decoded PNG at least 100x100 pixels. Other rows have weight 1.

## Calibration

Pending the three real Claude Code default-model runs. Failures are retained.

## Future version

Version 2 may add a second group-scale lens galaxy after single-lens calibration.
