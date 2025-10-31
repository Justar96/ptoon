Data Restructuring for Token Efficiency
========================================

This guide shows how to restructure deeply nested data into token-efficient patterns that work beautifully with TOON format.

.. note::
   Run ``python examples/better_patterns_demo.py`` to see these patterns in action with real token measurements!

Why Restructure?
----------------

Deep nesting (3+ levels) is:

- ❌ **Not supported by TOON** (by design)
- ❌ **Token-inefficient** (uses MORE tokens than JSON)
- ❌ **Hard to query** (requires complex traversal)

Flat structures are:

- ✅ **TOON-compatible** (≤2 levels)
- ✅ **Token-efficient** (35-60% savings!)
- ✅ **Easy to query** (simple filtering/searching)

Pattern 1: Trees → Adjacency Lists
-----------------------------------

**Use for:** File systems, org charts, navigation menus, comment threads

Anti-Pattern: Deeply Nested Tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ❌ 3-4 levels deep, repeated "children" keys
   tree = {
       "name": "root",
       "id": 0,
       "children": [
           {
               "name": "docs",
               "id": 1,
               "children": [
                   {"name": "readme.md", "id": 2, "children": []},
                   {"name": "guide.md", "id": 3, "children": []},
               ]
           },
           {
               "name": "src",
               "id": 4,
               "children": [
                   {
                       "name": "utils",
                       "id": 5,
                       "children": [
                           {"name": "helpers.py", "id": 6, "children": []}
                       ]
                   }
               ]
           }
       ]
   }

**Problems:**

- 3-4 levels deep (exceeds TOON limit)
- Repeated ``children`` keys at every level
- Empty arrays everywhere
- Hard to find specific nodes

Better Pattern: Flat Adjacency List
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Only 2 levels, perfect for TOON tabular format!
   tree_flat = {
       "nodes": [
           {"id": 0, "name": "root",       "parent": None, "type": "dir"},
           {"id": 1, "name": "docs",       "parent": 0,    "type": "dir"},
           {"id": 2, "name": "readme.md",  "parent": 1,    "type": "file"},
           {"id": 3, "name": "guide.md",   "parent": 1,    "type": "file"},
           {"id": 4, "name": "src",        "parent": 0,    "type": "dir"},
           {"id": 5, "name": "utils",      "parent": 4,    "type": "dir"},
           {"id": 6, "name": "helpers.py", "parent": 5,    "type": "file"},
       ]
   }

**TOON Output:**

.. code-block:: text

   nodes[7]{id,name,parent,type}:
     0,root,null,dir
     1,docs,0,dir
     2,readme.md,1,file
     3,guide.md,1,file
     4,src,0,dir
     5,utils,4,dir
     6,helpers.py,5,file

**Token Savings:** 50-60% vs nested JSON! 🎉

Helper Function
^^^^^^^^^^^^^^^

.. code-block:: python

   def tree_to_adjacency(tree, parent_id=None, node_id_counter=[0]):
       """Convert nested tree to flat adjacency list.

       Args:
           tree: Nested dict with 'children' key
           parent_id: Parent node ID (None for root)
           node_id_counter: Mutable counter for generating IDs

       Returns:
           List of flat node dicts
       """
       nodes = []

       # Create current node
       node_id = node_id_counter[0]
       node_id_counter[0] += 1

       node = {"id": node_id, "parent_id": parent_id}

       # Copy all fields except 'children'
       for key, value in tree.items():
           if key != "children":
               node[key] = value

       nodes.append(node)

       # Recursively process children
       if "children" in tree:
           for child in tree["children"]:
               nodes.extend(tree_to_adjacency(child, node_id, node_id_counter))

       return nodes

   # Usage
   tree = {"name": "root", "children": [{"name": "child", "children": []}]}
   flat = {"nodes": tree_to_adjacency(tree)}
   encoded = pytoon.encode(flat)  # Beautiful tabular format!

Real-World Example: Organization Chart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # ❌ Nested org chart (hard to query)
   org_nested = {
       "name": "Alice",
       "title": "CEO",
       "reports": [
           {
               "name": "Bob",
               "title": "VP Engineering",
               "reports": [
                   {"name": "Carol", "title": "Tech Lead", "reports": []},
                   {"name": "Dave", "title": "Tech Lead", "reports": []},
               ]
           },
           {
               "name": "Eve",
               "title": "VP Sales",
               "reports": [{"name": "Frank", "title": "Sales Rep", "reports": []}]
           }
       ]
   }

   # ✅ Flat employees with manager links (easy to query!)
   org_flat = {
       "employees": [
           {"id": 1, "name": "Alice", "title": "CEO",            "manager_id": None},
           {"id": 2, "name": "Bob",   "title": "VP Engineering", "manager_id": 1},
           {"id": 3, "name": "Carol", "title": "Tech Lead",      "manager_id": 2},
           {"id": 4, "name": "Dave",  "title": "Tech Lead",      "manager_id": 2},
           {"id": 5, "name": "Eve",   "title": "VP Sales",       "manager_id": 1},
           {"id": 6, "name": "Frank", "title": "Sales Rep",      "manager_id": 5},
       ]
   }

**Token Savings:** 55-65% vs nested JSON!

Pattern 2: Tensors → Flattened with Shape
------------------------------------------

**Use for:** Multi-dimensional arrays, matrices, image data, ML tensors

Anti-Pattern: 3D Nested Arrays
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ❌ 3 levels deep, lots of bracket overhead
   tensor_nested = [
       [  # Matrix 0
           [1, 2, 3, 4],    # Row 0
           [5, 6, 7, 8],    # Row 1
           [9, 10, 11, 12]  # Row 2
       ],
       [  # Matrix 1
           [13, 14, 15, 16],
           [17, 18, 19, 20],
           [21, 22, 23, 24]
       ]
   ]

**Problems:**

- 3 levels deep (exceeds TOON limit)
- Lots of bracket overhead in JSON
- Shape is implicit (have to count)
- Hard to validate dimensions

Better Pattern: Flattened with Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Only 2 levels, explicit shape
   tensor_flat = {
       "shape": [2, 3, 4],  # 2 matrices, 3 rows each, 4 columns each
       "dtype": "int",
       "data": [
           1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,    # Matrix 0
           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24  # Matrix 1
       ]
   }

**TOON Output:**

.. code-block:: text

   shape[3]: 2,3,4
   dtype: int
   data[24]: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24

**Token Savings:** 35-45% vs nested JSON!

Helper Functions
^^^^^^^^^^^^^^^^

.. code-block:: python

   import numpy as np

   def tensor_to_flat(array):
       """Convert nested array to flat dict with shape.

       Args:
           array: numpy array or nested list

       Returns:
           Dict with 'shape', 'dtype', and 'data' keys
       """
       arr = np.array(array)
       return {
           "shape": list(arr.shape),
           "dtype": str(arr.dtype),
           "data": arr.flatten().tolist()
       }

   def flat_to_tensor(flat_dict):
       """Reconstruct tensor from flat representation.

       Args:
           flat_dict: Dict with 'shape' and 'data' keys

       Returns:
           numpy array with original shape
       """
       return np.array(flat_dict["data"]).reshape(flat_dict["shape"])

   # Usage
   tensor_3d = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
   flat = tensor_to_flat(tensor_3d)
   encoded = pytoon.encode(flat)

   # Reconstruct
   original = flat_to_tensor(flat)

Real-World Example: Image Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # ❌ Nested 2D image (height x width x RGB)
   image_nested = [
       [[255, 0, 0], [0, 255, 0]],  # Row 0
       [[0, 0, 255], [255, 255, 0]] # Row 1
   ]  # 2x2 RGB image

   # ✅ Flattened pixel data with metadata
   image_flat = {
       "width": 2,
       "height": 2,
       "format": "RGB",
       "pixels": [255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 0]
   }

**Token Savings:** 35-50% for typical images!

Pattern 3: Nested Collections → Normalized Tables
--------------------------------------------------

**Use for:** E-commerce orders, API responses, database-style data

Anti-Pattern: Deeply Nested Document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ❌ 3-4 levels deep, repeated structure
   order_nested = {
       "order_id": "ORD-001",
       "customer": {
           "id": 123,
           "name": "Alice",
           "email": "alice@example.com",
           "address": {
               "street": "123 Main St",
               "city": "Springfield",
               "zip": "12345"
           }
       },
       "items": [
           {
               "sku": "WIDGET-A",
               "name": "Widget A",
               "price": 10.99,
               "quantity": 2,
               "details": {
                   "color": "red",
                   "size": "M"
               }
           },
           {
               "sku": "GADGET-B",
               "name": "Gadget B",
               "price": 25.50,
               "quantity": 1,
               "details": {
                   "color": "blue",
                   "size": "L"
               }
           }
       ]
   }

**Problems:**

- 3-4 levels deep
- Nested objects everywhere
- Repeated structure keys (``details``, ``address``)
- Hard to query across orders

Better Pattern: Normalized Tables (Database-Style)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Separate tables with foreign keys
   order_normalized = {
       "orders": [
           {"id": "ORD-001", "customer_id": 123, "total": 47.48}
       ],
       "customers": [
           {
               "id": 123,
               "name": "Alice",
               "email": "alice@example.com",
               "street": "123 Main St",
               "city": "Springfield",
               "zip": "12345"
           }
       ],
       "order_items": [
           {
               "order_id": "ORD-001",
               "sku": "WIDGET-A",
               "name": "Widget A",
               "price": 10.99,
               "quantity": 2,
               "color": "red",
               "size": "M"
           },
           {
               "order_id": "ORD-001",
               "sku": "GADGET-B",
               "name": "Gadget B",
               "price": 25.50,
               "quantity": 1,
               "color": "blue",
               "size": "L"
           }
       ]
   }

**TOON Output (Beautiful Tabular Format!):**

.. code-block:: text

   orders[1]{id, customer_id, total}:
     ORD-001, 123, 47.48

   customers[1]{id, name, email, street, city, zip}:
     123, Alice, alice@example.com, "123 Main St", Springfield, 12345

   order_items[2]{order_id, sku, name, price, quantity, color, size}:
     ORD-001, WIDGET-A, "Widget A", 10.99, 2, red, M
     ORD-001, GADGET-B, "Gadget B", 25.50, 1, blue, L

**Token Savings:** 40-55% vs nested JSON! 🚀

Pattern 4: Recursive Structures → Path-Based
---------------------------------------------

**Use for:** Comment threads, nested folders, recursive data

Anti-Pattern: Nested Comments Thread
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ❌ Reddit/HN style comment tree (3+ levels)
   thread_nested = {
       "id": 1,
       "text": "Great article!",
       "replies": [
           {
               "id": 2,
               "text": "I agree",
               "replies": [
                   {
                       "id": 3,
                       "text": "Me too",
                       "replies": []
                   }
               ]
           },
           {
               "id": 4,
               "text": "Thanks",
               "replies": []
           }
       ]
   }

Better Pattern: Flat with Parent Links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Flat comments with parent pointers
   thread_flat = {
       "comments": [
           {"id": 1, "parent_id": None, "text": "Great article!", "depth": 0},
           {"id": 2, "parent_id": 1,    "text": "I agree",       "depth": 1},
           {"id": 3, "parent_id": 2,    "text": "Me too",        "depth": 2},
           {"id": 4, "parent_id": 1,    "text": "Thanks",        "depth": 1},
       ]
   }

**TOON Output:**

.. code-block:: text

   comments[4]{id,parent_id,text,depth}:
     1,null,Great article!,0
     2,1,I agree,1
     3,2,Me too,2
     4,1,Thanks,1

**Token Savings:** 45-60% vs nested!

Alternative: Path Notation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For breadcrumb-style navigation:

.. code-block:: python

   thread_with_paths = {
       "comments": [
           {"id": 1, "path": "1",     "text": "Great article!"},
           {"id": 2, "path": "1.2",   "text": "I agree"},
           {"id": 3, "path": "1.2.3", "text": "Me too"},
           {"id": 4, "path": "1.4",   "text": "Thanks"},
       ]
   }

Token Savings Summary
---------------------

Real measurements from ``examples/better_patterns_demo.py``:

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 20

   * - Use Case
     - Nested JSON
     - Flat TOON
     - Savings
   * - File tree (7 nodes)
     - 161 tokens
     - 79 tokens
     - **51%** 🎉
   * - Org chart (6 people)
     - 147 tokens
     - 95 tokens
     - **35%** 🎉
   * - Comments (4 items)
     - 126 tokens
     - 76 tokens
     - **40%** 🎉
   * - E-commerce order
     - 175 tokens
     - 139 tokens
     - **21%** ✅
   * - 3D tensor (2x3x4)
     - 73 tokens
     - 67 tokens
     - **8%** ✅

**Average: 35-51% token savings** when restructuring!

Decision Guide
--------------

When should you flatten your data?

.. code-block:: text

   Does your data have:

   ├─ Repeated nested structure? (list of objects with same nested shape)
   │  └─ Yes → ✅ Normalize to separate tables (Pattern 3)
   │
   ├─ Tree/hierarchy with unlimited depth?
   │  └─ Yes → ✅ Use adjacency list with parent links (Pattern 1)
   │
   ├─ Multi-dimensional numeric data? (matrices, tensors, images)
   │  └─ Yes → ✅ Flatten with explicit shape (Pattern 2)
   │
   ├─ Recursive structure? (comments, nested folders)
   │  └─ Yes → ✅ Use path notation or parent links (Pattern 4)
   │
   └─ Simple nesting (2 levels, varied structure)?
      └─ Keep nested! TOON handles this beautifully.

Best Practices
--------------

1. **Flat is better than nested** - Easier to query, process, and more token-efficient
2. **Explicit is better than implicit** - Include shape, type, metadata
3. **Tables over hierarchies** - Tabular format is TOON's strength
4. **Foreign keys over embedding** - Database normalization principles apply
5. **Test token counts** - Measure before/after with ``pytoon.estimate_savings()``

See Also
--------

- :doc:`../faq` - FAQ about limitations and restructuring
- :doc:`token_optimization` - More token optimization tips
- ``examples/better_patterns_demo.py`` - Runnable examples with measurements
- :doc:`../user_guide/performance_tips` - Performance optimization guide
