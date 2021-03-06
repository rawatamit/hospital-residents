
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = "END ID INT PARTITION_A PARTITION_B PREFERENCE_LISTS_A PREFERENCE_LISTS_Bgraph : nodes nodes edges edgesnodes : PARTITION_A pvertex_list ';' ENDnodes : PARTITION_B pvertex_list ';' ENDpvertex_list : pvertex_list ',' pvertexpvertex_list : pvertexpvertex : IDpvertex : ID '(' INT ')'pvertex : ID '(' INT ',' INT ')'vertex_list : vertex_list ',' IDvertex_list : IDedges : PREFERENCE_LISTS_A preference_lists ENDedges : PREFERENCE_LISTS_B preference_lists ENDpreference_lists : preference_lists pref_listpreference_lists : pref_listpref_list : ID ':' vertex_list ';'"
    
_lr_action_items = {'PARTITION_A':([0,2,22,25,],[3,3,-2,-3,]),'PARTITION_B':([0,2,22,25,],[4,4,-2,-3,]),'$end':([1,17,26,29,],[0,-1,-11,-12,]),'ID':([3,4,11,12,14,18,19,21,27,28,35,36,],[8,8,20,20,8,20,-14,20,-13,32,-15,38,]),'PREFERENCE_LISTS_A':([5,10,22,25,26,29,],[11,11,-2,-3,-11,-12,]),'PREFERENCE_LISTS_B':([5,10,22,25,26,29,],[12,12,-2,-3,-11,-12,]),';':([6,7,8,9,23,30,32,33,37,38,],[13,-5,-6,16,-4,-7,-10,35,-8,-9,]),',':([6,7,8,9,23,24,30,32,33,37,38,],[14,-5,-6,14,-4,31,-7,-10,36,-8,-9,]),'(':([8,],[15,]),'END':([13,16,18,19,21,27,35,],[22,25,26,-14,29,-13,-15,]),'INT':([15,31,],[24,34,]),':':([20,],[28,]),')':([24,34,],[30,37,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'graph':([0,],[1,]),'nodes':([0,2,],[2,5,]),'pvertex_list':([3,4,],[6,9,]),'pvertex':([3,4,14,],[7,7,23,]),'edges':([5,10,],[10,17,]),'preference_lists':([11,12,],[18,21,]),'pref_list':([11,12,18,21,],[19,19,27,27,]),'vertex_list':([28,],[33,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> graph","S'",1,None,None,None),
  ('graph -> nodes nodes edges edges','graph',4,'p_graph','graph_parser.py',10),
  ('nodes -> PARTITION_A pvertex_list ; END','nodes',4,'p_partition_A','graph_parser.py',15),
  ('nodes -> PARTITION_B pvertex_list ; END','nodes',4,'p_partition_B','graph_parser.py',20),
  ('pvertex_list -> pvertex_list , pvertex','pvertex_list',3,'p_pvertex_list','graph_parser.py',26),
  ('pvertex_list -> pvertex','pvertex_list',1,'p_pvertex_list_terminating','graph_parser.py',31),
  ('pvertex -> ID','pvertex',1,'p_pvertex_one','graph_parser.py',37),
  ('pvertex -> ID ( INT )','pvertex',4,'p_pvertex_capacity_upper','graph_parser.py',42),
  ('pvertex -> ID ( INT , INT )','pvertex',6,'p_pvertex_capacity_upper_and_lower','graph_parser.py',47),
  ('vertex_list -> vertex_list , ID','vertex_list',3,'p_vertex_list','graph_parser.py',52),
  ('vertex_list -> ID','vertex_list',1,'p_vertex_list_terminating','graph_parser.py',57),
  ('edges -> PREFERENCE_LISTS_A preference_lists END','edges',3,'p_preference_lists_A','graph_parser.py',62),
  ('edges -> PREFERENCE_LISTS_B preference_lists END','edges',3,'p_preference_lists_B','graph_parser.py',67),
  ('preference_lists -> preference_lists pref_list','preference_lists',2,'p_preference_lists','graph_parser.py',72),
  ('preference_lists -> pref_list','preference_lists',1,'p_preference_lists_terminating','graph_parser.py',77),
  ('pref_list -> ID : vertex_list ;','pref_list',4,'p_pref_list','graph_parser.py',82),
]
