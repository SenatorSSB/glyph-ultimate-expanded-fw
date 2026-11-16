# Authorized GOPT and Switch USB integration

On 2026-11-16 the owner directed integration of the tested USB repair and GOPT into `configurator`.

The live remote baseline was `2bcb5104054f64d8b9c1af9dd1be4a974112f8ec`. The integrated ancestry contains reviewed GOPT `79475873f2c5f4b84e77bf9f94ab39779ffc69a5`, tested USB source `5dfc4cc26ca27d1de15c80e2a59f9637052f1b5c`, and physical acceptance record `ac3dcde0`. All production/build inputs remain identical to the tested USB source. Canonical integration uses a fast-forward preserving this history.

The original Nintendo Switch / Ultimate trial passes for the owner's reported sticks and gamepad buttons. Postinstall Configurator reports `5dfc4cc2` and verifies complete API-visible Config and 27-profile preservation. The exact tested UF2 remains `de793f3469e8d88de31fb6f85d50bacd203b13928f1333ae5b291557c84b1518`. Prior GOPT acceptance retains its recorded scope. [Physical result](PHYSICAL_RESULT.json) · [Qualification](QUALIFICATION.md)

The final integration receipt commit uses the accepted `[skip ci]` publication procedure. The inspected push workflow otherwise can build, postprocess and upload firmware. Existing source/build and independent reviews remain the evidence for these unchanged production inputs. This integration does not produce a newly qualified rebuilt image. Hosted validation remains as recorded in the qualification receipt, including the aggregate timeout limitation.

Public beta distribution, a release/tag and additional hardware installation require their corresponding owner direction. Fresh installation, Windows XInput, Switch 2 and recovery retain the recorded qualification limits.
