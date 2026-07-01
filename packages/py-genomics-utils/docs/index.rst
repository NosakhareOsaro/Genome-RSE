genomics-utils
===============

Small bioinformatics utilities: a VCF annotation helper, a minimal FHIR
R4 resource validator, and a MultiQC plugin.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api

Scope notes
-----------

- The VCF annotation helper does not consult any external annotation
  database; it classifies variant types and computes Ts/Tv statistics
  from the VCF file's own contents.
- The FHIR validator performs **structural** validation of a minimal
  ``Patient``/``Observation`` subset only — not full FHIR conformance
  validation. See :mod:`genomics_utils.fhir_validate` for details.

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
