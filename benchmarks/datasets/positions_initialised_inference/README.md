# Simulated imaging and matching lensed positions

100 x 100 pixels, 0.1 arcsec/pixel; Gaussian PSF supplied in `psf.fits`.
Lens/source redshifts 0.5/1.0. `positions.json` is a library `PointDataset`
with four (y,x) image positions and 0.05 arcsec errors, no fluxes/time delays.

Use an Isothermal mass at (0,0), an ExternalShear field and circular Sersic
lens/source light; the lens light is centred at (0,0). Other parameters are
unknown. Fit with a 2.5 arcsec circular mask and uniform oversampling 2.
No `info.json` or true model is supplied. The maintainer regeneration script
and reference posterior are hidden from benchmark sessions.
