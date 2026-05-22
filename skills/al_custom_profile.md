---
name: al_custom_profile
description: Write a new light or mass profile subclass for use in PyAutoGalaxy / PyAutoLens models. Walks the user through subclassing the right base class, implementing the required `image_2d_from`, `convergence_2d_from`, or `deflections_yx_2d_from` methods, registering parameter defaults / priors, and using the new profile in an `af.Model`. For *combining* existing profiles (bulge + disk, basis expansions) the standard `af.Model` composition already covers it — don't bootstrap a new profile if you only need composition.
---

# Adding a custom light or mass profile

Sometimes you need a profile PyAutoGalaxy doesn't ship. Maybe an oblate Sersic with a
specific isophote twist, or an exotic mass distribution from a dark-matter model.
PyAutoGalaxy's profile machinery is designed for subclassing — you implement one or
two methods on a base class, register defaults, and the new profile drops into
`af.Model` like any built-in.

Canonical reference: `autolens_workspace:scripts/guides/advanced/add_a_profile.py`.

## Ask

- *"Light profile or mass profile?"* — different base classes, different required
  methods.
- *"Can you write down the analytic form?"* — if yes, this skill applies. If you
  only have a numerical implementation, see the "numerical profile" branch.
- *"Is this for shared use (PR upstream) or one-off for this analysis?"* — affects
  where the file lives and whether to add tests.

## Branch — custom light profile

Subclass `LightProfile` (or `LightProfileLinear` for a profile whose intensity is
solved during the fit). Implement `image_2d_from(grid)`:

```python
# work/my_profile.py
import numpy as np
import autogalaxy as ag
from autoconf.dictable import Dictable


class TwistedSersic(ag.LightProfile, Dictable):
    """Sersic light profile with isophote position-angle twist with radius."""

    def __init__(
        self,
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.0),
        intensity=1.0,
        effective_radius=1.0,
        sersic_index=2.0,
        twist_rate=0.0,
    ):
        super().__init__(centre=centre, ell_comps=ell_comps)
        self.intensity = intensity
        self.effective_radius = effective_radius
        self.sersic_index = sersic_index
        self.twist_rate = twist_rate

    def image_2d_from(self, grid, **kwargs):
        # Apply the elliptical + twisted transform manually, then evaluate Sersic.
        radii = self._radii_from_grid(grid)              # helper method
        intensity = self.intensity * np.exp(
            -self._b_n() * ((radii / self.effective_radius) ** (1.0 / self.sersic_index) - 1.0)
        )
        return intensity
```

Source citations:
- `PyAutoGalaxy:autogalaxy/profiles/light/abstract.py` — `LightProfile` base class
  and required interface.
- `PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py` — Sersic implementation
  to copy structure from.
- `PyAutoConf:autoconf/dictable.py` — `Dictable` mixin so the profile serialises to
  `tracer.json`.

Use in a model:

```python
import autofit as af
from work.my_profile import TwistedSersic

lens = af.Model(
    ag.Galaxy,
    redshift=0.5,
    bulge=af.Model(TwistedSersic),  # new profile, slots into the af.Model API
)
```

## Branch — custom mass profile

Subclass `MassProfile` and implement at least `convergence_2d_from(grid)` and
`deflections_yx_2d_from(grid)`. PyAutoGalaxy provides the integral helpers if the
deflection has no closed form.

```python
class CustomNFW(ag.MassProfile, Dictable):
    """NFW with a custom inner-slope tweak."""

    def __init__(self, centre=(0.0, 0.0), kappa_s=1.0, scale_radius=1.0, inner_slope=1.0):
        super().__init__(centre=centre, ell_comps=(0.0, 0.0))
        self.kappa_s = kappa_s
        self.scale_radius = scale_radius
        self.inner_slope = inner_slope

    def convergence_2d_from(self, grid, **kwargs):
        r = self._radii_from_grid(grid) / self.scale_radius
        return self.kappa_s / (r ** self.inner_slope * (1.0 + r) ** (3.0 - self.inner_slope))

    def deflections_yx_2d_from(self, grid, **kwargs):
        # Integrate the convergence — or derive an analytic form if available.
        # See PyAutoGalaxy:autogalaxy/profiles/mass/dark/nfw.py for the canonical NFW.
        raise NotImplementedError("Wire up your deflection integral here.")
```

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/abstract.py` — interface.
`PyAutoGalaxy:autogalaxy/profiles/mass/dark/nfw.py` — canonical NFW for shape.

For the physics of what each method represents (convergence = surface mass density,
deflection = angular shift from the mass model), read
[`wiki/core/concepts/mass_profiles.md`](../wiki/core/concepts/mass_profiles.md).

## Branch — numerical-only profile

If you only have a tabulated profile (e.g. from an N-body simulation), wrap it in a
class that interpolates on the grid:

```python
from scipy.interpolate import RegularGridInterpolator

class TabulatedConvergence(ag.MassProfile, Dictable):
    def __init__(self, centre, table_path):
        super().__init__(centre=centre, ell_comps=(0.0, 0.0))
        self._interp = self._load_table(table_path)

    def convergence_2d_from(self, grid, **kwargs):
        return self._interp((grid[:, 0], grid[:, 1]))
```

You'll still need a deflection method; the integral form from `MassProfile` can do
it numerically but at a runtime cost. Profile your fit if this is slow.

## Priors and defaults

For the new profile to play nicely in `af.Model`, give each parameter a sensible
default prior. Either set it in the model declaration:

```python
profile = af.Model(TwistedSersic)
profile.twist_rate = af.UniformPrior(lower_limit=-1.0, upper_limit=1.0)
```

Or — for repeated use — add a default-priors YAML under
`PyAutoGalaxy:autogalaxy/config/priors/` keyed by class name. The conf system reads
it automatically.

## Verification

```python
# Sanity: image_2d_from returns the right shape and finite values.
import autoarray as aa
grid = aa.Grid2D.uniform(shape_native=(50, 50), pixel_scales=0.05)
prof = TwistedSersic(centre=(0.0, 0.0), intensity=1.0, effective_radius=0.5, sersic_index=2.0, twist_rate=0.1)
img = prof.image_2d_from(grid=grid)
assert img.shape == (2500,) and np.isfinite(img).all()
```

For mass profiles, also sanity-check `convergence_2d_from` against a known case (set
`twist_rate=0`, your custom Sersic should match the built-in Sersic).

## Combine

- [`al_build_imaging_model`](./al_build_imaging_model.md) — plug the new profile
  into a full model.
- [`al_simulate_dataset`](./al_simulate_dataset.md) — synthesise a dataset using the
  new profile, fit it back, confirm recovery.
- [`al_update_wiki`](./al_update_wiki.md) — if the profile becomes a permanent
  fixture, add it to the wiki catalogue (`wiki/core/api/light_profile_catalog.md` or
  `mass_profile_catalog.md`).

## Further reading

- **Student / new to lensing** — [HowToLens: Grids, light profiles, and galaxy
  objects](https://github.com/PyAutoLabs/HowToLens/blob/main/notebooks/chapter_1_introduction/tutorial_1_grids_and_galaxies.ipynb):
  how built-in profiles plug into `Galaxy` and grids — the API your custom profile
  has to fit into.
- **General reference** — [RTD: Model cookbook](https://pyautolens.readthedocs.io/en/latest/general/model_cookbook.html):
  systematic model-composition reference; covers using non-standard profiles
  inside `Model` and `Collection`.
- **Experienced PyAutoLens user** — [workspace/lens: guides/profiles/light.py](https://github.com/Jammy2211/autolens_workspace/blob/main/scripts/guides/profiles/light.py):
  catalog of the built-in light profiles in `al.lp.*` — the patterns your subclass
  should match.
