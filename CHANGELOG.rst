Changelog
=========

v0.2
----

New
~~~

- Support EC2 instances with no VPC ID. [Ash Wilson]

  Uses multi-stage build in Dockerfile to consolidate testing and
  container image build.

  closes #2, closes #4

Changes
~~~~~~~

- Changed HALO_API_HOST to HALO_API_HOSTNAME. [Ash Wilson]

  This changes the behavior of the tool. HALO_API_HOST was used
  to define the hostname the SDK used to reach the Halo API.
  Going forward, users should transition to using HALO_API_HOSTNAME
  for this.

  The default value of `api.cloudpassage.com` is now set, in the
  Dockerfile, for HALO_API_HOSTNAME. Any users that currently use
  this tool against MTG will not need to change anything. Non-MTG
  users will need to update their container launch environment
  variables.

  Closes #7


