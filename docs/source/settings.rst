Custom settings
===============

You can use any of the settings understood by `Django
<https://docs.djangoproject.com/en/dev/ref/settings/>`_ and **django-ca**
provides some of its own settings.

From Djangos settings, you especially need to configure ``DATABASES``,
``SECRET_KEY``, ``ALLOWED_HOSTS`` and ``STATIC_ROOT``.

All settings used by **django-ca** start with the ``CA_`` prefix. Settings are
also documented at :file:`ca/ca/localsettings.py.example`
(`view on git
<https://github.com/mathiasertl/django-ca/blob/master/ca/ca/localsettings.py.example>`_).

CA_ALLOW_CA_CERTIFICATES
   Default: ``False``

   Determines if the root CA is allowed to issue certificates that themself can
   be used as a CA. Setting this to ``True`` will enable a ``ca`` profile that
   can be used in both the admin webinterface or with ``manage.py sign_cert
   --ca``. On a certificate level, this sets the `basicConstraints` x509
   extension to ``CA:TRUE``.

CA_CRL_DISTRIBUTION_POINTS
   Default: ``[]``

   A list of valid URLs for a Certificate Revokation Lists. See :doc:`crl` for
   more information.

   .. WARNING:: Do not set this value unless you actually plan on hosting the
      CRL. CRL-enabled clients will refuse to connect if the CRL cannot be found.

CA_CRL_SETTINGS
   Default: ``None``

   A dictionary containing settings for how to generate the CRLs. It acts as a
   default ``manage.py dump_crl`` and, if set, causes **django-ca** to
   regenerate the CRL whenever a certificate is revoked. It contains the
   following keys:

   path (mandatory)
      Path to dump the CRL to.
   days
      The number of days until the next update of this CRL. The default is one
      day. Note that the lower limit of one day is a pyOpenSSL restriction.
   type
      The export format, either ``PEM``, ``ASN1`` or ``TEXT``. The default is
      ``PEM``.
   digest
      The name of the message digest to use. The default is the value of the
      ``CA_DIGEST_ALGORITHM`` setting.

   A full example::

      CA_CRL_SETTINGS = {
         'path': '/var/www/ca.example.com/ca.crl',
         'days': 3,  # We recreate the CRL every three days
         'type': 'ASN1',
         'digest': 'sha256',
      }

CA_DEFAULT_EXPIRES
   Default: ``730``

   The default time, in days, that any signed certificate expires.

CA_DEFAULT_PROFILE
   Default: ``webserver``

   The default profile to use.

CA_DEFAULT_SUBJECT
   Default: ``{}``

   The default subject to use. The keys of this dictionary are the valid fields
   in X509 certificate subjects. Example::

      CA_DEFAULT_SUBJECT = {
         'C': 'AT',
         'ST': 'Vienna',
         'L': 'Vienna',
         'O': 'HTU Wien',
         'OU': 'Fachschaft Informatik',
         'emailAddress': 'user@example.com',
      }

CA_DIGEST_ALGORITHM
   Default: ``"sha512"``

   The default digest algorithm used to sign certificates. You may want to use
   ``"sha256"`` for older (pre-2010) clients. Note that this setting is also
   used by the ``init_ca`` command, so if you have any clients that do not
   understand sha512 hashes, you should change this beforehand.

CA_DIR
   Default: ``"ca/files"``

   Where the root certificate is stored. The default is a ``files`` directory
   in the same location as your ``manage.py`` file.

CA_ISSUER
   Default: ``None``

   Add a ``caIssuers`` value to the ``authorityInfoAccess`` x509 extension of
   signed certificates. This is usually a URL where further information about
   the CA can be retrieved.

CA_ISSUER_ALT_NAME
   Default: ``None``

   Set a value for the ``issuerAltName`` x509 extension. By default, the
   CommonName from the root certificate is copied (the last parameter of the
   ``init_ca`` command).

CA_OCSP
   Default: ``None``

   Location of an OCSP responder. This will add the ``OCSP`` value to the
   ``authorityInfoAccess`` x509 extension of signed certificates. See
   :ref:`ocsp` for more information.

   .. WARNING:: Do not set this value unless you actually plan on hosting an
      OCSP responder. OCSP-enabled clients will refuse to connect if there is
      no actual OCSP service.

CA_OCSP_INDEX_PATH
   Default: ``None``

   A path to dump the OCSP index to. Setting this value will cause
   **django-ca** to regenerate the index whenever you revoke a certificate.

CA_PROFILES
   Default: ``{}``

   Profiles determine the default values for the ``keyUsage``,
   ``extendedKeyUsage`` and ``basicConstraints`` x509 extensions. In short,
   they determine how your certificate can be used, be it for server and/or
   client authentication, e-mail signing or anything else. By default,
   **django-ca** provides these profiles:

   =========== ======================================== =======================
   Profile     keyUsage                                 extendedKeyUsage
   =========== ======================================== =======================
   client      digitalSignature                         clientAuth
   server      digitalSignature, keyAgreement           clientAuth, serverAuth
               keyEncipherment
   webserver   digitalSignature, keyAgreement           serverAuth
               keyEncipherment
   enduser     dataEncipherment, digitalSignature,      clientAuth,
               keyEncipherment                          emailProtection,
                                                        codeSigning
   ocsp        nonRepudiation, talSignature,            OCSPSigning
               keyEncipherment
   ca          cRLSign, keyCertSign
   =========== ======================================== =======================

   Further more,

   * The ``keyUsage`` attribute is marked as critical.
   * The ``extendedKeyUsage`` attribute is marked as non-critical.
   * All profiles have their ``basicConstraints`` marked as critical
     ``CA:FALSE``, except the "ca" profile, which has critical ``CA:TRUE``.

   This should be fine for most usecases. But you can use the ``CA_PROFILES``
   setting to either update or disable existing profiles or add new profiles
   that you like. For that, set ``CA_PROFILES`` to a dictionary with the keys
   defining the profile name and the value being either:

   * ``None`` to disable an existing profile.
   * A dictionary defining the profile. If the name of the profile is an
     existing profile, the dictionary is updated, so you can ommit a value to
     leave it as the default. The possible keys are:

     ====================== ======================================================================
     key                    Description
     ====================== ======================================================================
     ``"keyUsage"``         The ``keyUsage`` X509 extension.
     ``"extendedKeyUsage"`` The ``extendedKeyUsage`` X509 extension.
     ``"desc"``             A human-readable description, shows up with "sing_cert -h" and in the
                            webinterface profile selection.
     ``"basicConstraints"`` The ``basicConstraints`` X509 extension.
     ``"subject"``          The default subject to use. If ommited, ``CA_DEFAULT_SUBJECT`` is
                            used.
     ``"cn_in_san"``        If to include the CommonName in the subjectAltName by default. The
                            default value is ``True``.
     ====================== ======================================================================

   Here is a full example:

     .. code-block:: python

         CA_DEFAULT_PROFILES = {
             'client': {
                 'desc': _('Nice description.'),
                 'basicConstraints': {
                     'critical': True,
                     'value': 'CA:FALSE',
                 },
                 'keyUsage': {
                     'critical': True,
                     'value': [
                        'digitalSignature',
                     ],
                 },
                 'extendedKeyUsage': {
                     'critical': False,
                     'value': [
                        'clientAuth',
                     ],
                  },
                  'subject': {
                     'C': 'AT',
                     'L': 'Vienna',
                  }
              },

              # We really don't like the "ocsp" profile, so we remove it.
              'ocsp': None,
         }
