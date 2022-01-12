Change Log
==========

2.X.X
-----

* Fixed issue of highwire elements storing escaped `content` as `bytes`. [#50](https://github.com/unt-libraries/pyuntl/pull/50)
* Replaced deprecated `cgi.escape` with `html.escape`. [#50](https://github.com/unt-libraries/pyuntl/pull/50)
* Moved the logic of FormGenerator.get_vocabularies to a new function, which is now called by the deprecated
  FormGenerator.get_vocabularies method and by retrieve_vocab.
* Modified new get_vocabularies function to use retries when retrieving the vocabularies, as well as caching them
  locally.

2.0.0
-----

* Upgraded to Python 3. [#18](https://github.com/unt-libraries/pyuntl/issues/18)
* Removed automatic addition of trailing period for LCSH. [#39](https://github.com/unt-libraries/pyuntl/issues/39)
* Removed etd_ms support which is not used by pyuntl. [#29](https://github.com/unt-libraries/pyuntl/issues/29)
* Added make_hidden, make_unhidden, is_hidden methods. [#37](https://github.com/unt-libraries/pyuntl/issues/37)
* Added support for JSON serializations. [#38](https://github.com/unt-libraries/pyuntl/issues/38)


1.0.2
-----

* Updated UNTL_USAGE_LINK setting to point to current help pages.
* Fixed a few flake8 issues relating to string comparisons.


1.0.1
-----

* Fixed hardcoding of http scheme in permalinks by dc_structure.identifier_director. [#11](https://github.com/unt-libraries/pyuntl/issues/11)


1.0.0
-----

* Initial release.
