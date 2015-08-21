pyuntl
=========

Python module for reading and writing UNTL metadata records.

```python
>>> from pyuntl.untl_structure import PYUNTL_DISPATCH
>>> from pyuntl.untldoc import untlpydict2xmlstring, untlpy2dict
>>> record = PYUNTL_DISPATCH["metadata"]()
>>> title = PYUNTL_DISPATCH["title"]()
>>> title.set_qualifier("officialtitle")
>>> title.set_content("This is the title for the record")
>>> record.add_child(title)
>>> print untlpydict2xmlstring(untlpy2dict(record))
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
  <title qualifier="officialtitle">This is the title for the record</title>
</metadata>
```
License
-------

See LICENSE.txt


Acknowledgements
----------------

_pyuntl_ was developed at the UNT Libraries and has been worked on by a number of developers over the years including:

Brandon Fredericks  

[Kurt Nordstrom](https://github.com/kurtnordstrom)  

[Joey Liechty](https://github.com/yeahdef)  

[Lauren Ko](https://github.com/ldko)  

[Mark Phillips](https://github.com/vphill)  

If you have questions about the project feel free to contact Mark Phillips at mark.phillips@unt.edu.
