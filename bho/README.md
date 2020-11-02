# Process BHO topographical dictionaries

The [BHO topographical dictionaries](https://www.british-history.ac.uk/search/series/topographical-dict) contain detail topographical accounts of places, parishes, and counties in Scotland, Wales, and England. The data is organised as follows:
```bash
topographical_dictionaries/
├── England
│   ├── 50740.xml
│   ├── 50741.xml
│   ├── 50742.xml
│   ├── ...
├── Scotland
│   ├── 44117.xml
│   ├── ...
└── Wales
    ├── 47793.xml
    ├── ...
```
The xml format is basic but a bit messy.

A copy of the data is in [Azure](https://lwmincomingbho.blob.core.windows.net/topodictionariesbho/topographical%20dictionaries.zip), and in the `toponymVM` virtual machine, in `/resources/bho/`.

Notebook [parse_bho_xml.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/dev/bho/parse_bho_xml.ipynb) takes the unzipped `topographical_dictionaries` directory as input (stored in `/resources/bho/`) and outputs a nested dictionary, e.g.:
```
{5:
  {'report_title': 'Abbas-Combe - Aberystwith',
   'place_name': 'Abbertoft',
   'description': '<para id="p5">ABBERTOFT, a hamlet, in the parish of Willoughby, union of Spilsby, Wold division of the hundred of Calceworth, parts of Lindsey, county of Lincoln, 7 miles (S. E.) from Alford; containing 23 inhabitants. This place, called also Habertoft, lies in the south-eastern portion of the parish, and is one of several hamlets within its limits. The Orby drain passes in an eastern direction here.</para>',
   'filepath': '/resources/bho/England/50741.xml'},
}
```
... where the outer key is the id of the entry (incremental, not provided by BHO). In the inner dictionary, `report_title` is the first and last entry in the section (see section title in https://www.british-history.ac.uk/topographical-dict/england/pp1-5), `place_name` is the name of the location in the entry, `description` is the text of the entry, the actual content (I haven't cleaned the xml tags in case we need them later), and `filepath` keeps the path of the file where the entry comes from.

This is then cleaned, resultin in a csv file with 18631 rows and with the following columns:
* **id:** incremental id (there is no ID in the original dataset)
* **title:** title of the dictionary entry (it's not unique, therefore can't be used as ID)
* **toponyms:** toponyms of the location in this dictionary entry, extracted from the entry itself.
* **contextwords:** words from the title that are not part of the toponym, but can help disambiguate it (e.g. to which saint the parish is dedicated)
* **redirected:** if the dictionary entry is actually a redirection (e.g. _"Abberbury, county Salop.—See Alberbury."_), in which case most fields will be left empty.
* **content:** The content of the entry.

Example:
```
id,title,toponyms,contextwords,redirected,content
1,"Abbas-Combe, or Temple-Combe (St. Mary)","['Temple-Combe', 'Abbas-Combe']",['St. Mary'],False,"[""ABBAS-COMBE, or Temple-Combe (St. Mary), a parish, in the union of Wincanton, hundred of Horethorne, E. division of Somerset, 4½ miles (S. by W.) from Wincanton, on the road to Blandford; containing 461 inhabitants. It derived the name of Temple-Combe from the military order of Knights Templars, who had an establishment here, which at the Dissolution possessed a revenue of £128. 7. 9. Some remains of the chapel attached to the old priory-house are still to be seen. The parish comprises by measurement 1884 acres of land; and contains good building-stone of the granite species, and limestone, both of which are quarried. The living is a rectory, valued in the king's books at £9. 9. 4½., and in the gift of the Rev. Thomas Fox: the tithes have been commuted for £370, and the glebe consists of 38 acres. The church has a tower on the south side of the nave. There is a place of worship for Independents.""]"
2,"Abberbury, county Salop.—See Alberbury.",[],[],True,[]
3,Abberley (St. Michael),['Abberley'],['St. Michael'],False,"['ABBERLEY (St. Michael), a parish, in the union of Martley, Lower division of the hundred of Doddingtree, Hundred-House and W. divisions of the county of Worcester, 12 miles (N. W. by N.) from Worcester; containing 559 inhabitants. This place, formerly Abbotsley, comprises 2564 acres of land, of which the arable and pasture are in equal portions, with about 70 acres of wood; the surface is well watered, and the soil rather above the average in fertility. The village is situated to the right of the road leading from Worcester to Ludlow, in a valley surrounded by hills whose summits afford delightful prospects: from one eminence eleven counties may be seen. Coal of good quality is wrought, and there are large quarries of excellent stone for building, and of stone for repairing roads. Abberley Hall, a beautiful Italian edifice, was purchased in 1844, with its surrounding demesne, from the Misses Bromley by the late J. L. Moilliet, Esq., by whom considerable improvements and alterations were made, in the purest taste; the whole of the interior was destroyed by fire on the 25th December 1845, but the exterior remains quite perfect, and the mansion is now undergoing complete repair.', ""The living is a rectory, valued in the king's books at £11. 10. 2½., and in the gift of Mrs. Moilliet; incumbent, the Rev. Francis Severne, whose tithes have been commuted for £333. 8., with two acres of glebe and a house. Certain impropriate tithes have been commuted for £100. The church is a neat ancient edifice, picturesquely situated on the east side of the village, and has a wood-shingle spire 99 feet high, with four bells; the architecture is of various styles, one of the windows presenting an excellent specimen of the Saxon arch. A school was founded under gifts made by Elizabeth and Victoria Walsh, in 1717; it has an income of £15 per annum, in addition to a house and garden: the school-house was rebuilt by Robert Bromley, Esq., in 1791. On Abberley hill, in the midst of a thickly-planted wood, stands an oak, said to have been a sapling from the oak-tree under which St. Augustine in the 6th century invited the Welsh bishops to a conference, as recorded by Milner in his Church History: the parent tree was afterwards consumed by fire. William Walsh, the poet, and a correspondent of Pope's and Addison's, was born in the parish in 1663: at the close of Pope's Essay on Criticism, are some touching lines to his memory.""]"
4,Abbertoft,['Abbertoft'],[],False,"['ABBERTOFT, a hamlet, in the parish of Willoughby, union of Spilsby, Wold division of the hundred of Calceworth, parts of Lindsey, county of Lincoln, 7 miles (S. E.) from Alford; containing 23 inhabitants. This place, called also Habertoft, lies in the south-eastern portion of the parish, and is one of several hamlets within its limits. The Orby drain passes in an eastern direction here.']"
```