from header_common import *
from header_operations import *
from header_parties import *
from header_items import *
from header_skills import *
from header_triggers import *
from header_troops import *

from module_constants import *

####################################################################################################################
#  Each trigger contains the following fields:
# 1) Check interval: How frequently this trigger will be checked
# 2) Delay interval: Time to wait before applying the consequences of the trigger
#    After its conditions have been evaluated as true.
# 3) Re-arm interval. How much time must pass after applying the consequences of the trigger for the trigger to become active again.
#    You can put the constant ti_once here to make sure that the trigger never becomes active again after it fires once.
# 4) Conditions block (list). This must be a valid operation block. See header_operations.py for reference.
#    Every time the trigger is checked, the conditions block will be executed.
#    If the conditions block returns true, the consequences block will be executed.
#    If the conditions block is empty, it is assumed that it always evaluates to true.
# 5) Consequences block (list). This must be a valid operation block. See header_operations.py for reference. 
####################################################################################################################

# Some constants for use below
merchant_inventory_space = 30
num_merchandise_goods = 36



triggers = [

# Refresh Merchants
  (0.0, 0, 168.0, [],
  [    
    (call_script, "script_refresh_center_inventories"),
  ]),

# Refresh Armor sellers
  (0.0, 0, 168.0, [],
  [    
    (call_script, "script_refresh_center_armories"),
  ]),

# Refresh Weapon sellers
  (0.0, 0, 168.0, [],
  [
    (call_script, "script_refresh_center_weaponsmiths"),
  ]),

# Refresh Horse sellers
  (0.0, 0, 168.0, [],
  [
    (call_script, "script_refresh_center_stables"),
  ]),
  

#############

 (1,0,ti_once,#temporary dirty solution
   [],
   [ (try_for_parties,":partie_no"),
		(party_get_template_id, ":cur_party_template", ":partie_no"),
          (eq, ":cur_party_template", "pt_looters"),
		(remove_party,":partie_no"),
	  (try_end),
   ]),



# (0,0,0,[(key_clicked,key_v)],
# [
	# (try_for_range,":i",0,42),
		# (troop_raise_skill,"trp_player",":i",-100),
	# (try_end),
	# (troop_raise_attribute,"trp_player",ca_strength,-100),
	# (troop_raise_attribute,"trp_player",ca_agility,-100),
	# (troop_raise_attribute,"trp_player",ca_intelligence,-100),
	# (troop_raise_attribute,"trp_player",ca_charisma,-100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_one_handed_weapon, -100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_two_handed_weapon, -100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_polearm, -100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_crossbow, -100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_throwing, -100),
	
# ]),

# (0,0,0,[(key_clicked,key_b)],
# [
	# (try_for_range,":i",0,42),
		# (troop_raise_skill,"trp_player",":i",100),
	# (try_end),
	
	# (troop_raise_attribute,"trp_player",ca_strength,100),
	# (troop_raise_attribute,"trp_player",ca_agility,100),
	# (troop_raise_attribute,"trp_player",ca_intelligence,100),
	# (troop_raise_attribute,"trp_player",ca_charisma,100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_one_handed_weapon, 100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_two_handed_weapon, 100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_polearm, 100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_crossbow, 100),
	# (troop_raise_proficiency_linear, "trp_player", wpt_throwing, 100),
# ]),




(0,0,0,[(key_clicked,key_m)],
[
# (assign,"$inventory_starting_item",10),
# (assign,"$selected_item",0),
(start_presentation, "prsnt_action_menu"),
]),

(0,0,0,[(key_clicked,key_n)],
[
(assign,"$g_fps",1),
]),


(0,0,0,[(key_clicked,key_tab)],
[
(start_presentation, "prsnt_player_stats"),
]),

(0.25,0,0,[(eq,"$g_fps",1),],[
	(try_begin),
		(neq,"$g_fps_start",1),
		(assign,"$g_fps_start",1),
		(assign,"$g_fps_counter",0),
	(else_try),
		(assign,"$g_fps_start",0),
		(assign,"$g_fps",0),
		(val_sub,"$g_fps_counter",2),#this is discovered experimentally
		(assign,reg1,"$g_fps_counter"),
		(display_message,"@FPS: {reg1}"),
	(try_end),
]),

(0,0,0,[(eq,"$g_fps_start",1),],[
	(val_add,"$g_fps_counter",1),
]),

(1,0,0,[],[#refresh the ping every 4 seconds
	(call_script,"script_send_int_to_server",mpcamp_event_ping,1,0),
]),

(3,0,0,[],[#refresh the inventory every 12 seconds
	(call_script,"script_send_int_to_server",mpcamp_event_get_inventory,0),
	(call_script,"script_send_int_to_server",mpcamp_event_get_gold,0),
]),

###no Pause mod ####
(0,0,0,[
	(neg|key_is_down,key_space),
	(eq,"$g_can_rest",1),
	],[
			(set_fixed_point_multiplier, 1000),
			(party_get_position,pos1,"p_main_party"),
			(position_get_x,":x",pos1),
			(position_get_y,":y",pos1),
			(try_begin),
				(eq,":x","$g_x"),
				(eq,":y","$g_y"),
				(assign,"$g_paused",1),
			(else_try),
				(assign,"$g_paused",0),
				(assign,"$g_x",":x"),
				(assign,"$g_y",":y"),
			(try_end),
			(try_begin),
				(eq,"$g_paused",1),
					(assign, "$g_player_icon_state", pis_normal),
					(rest_for_hours_interactive,999999,1,1),
			(try_end),
		
	
]),
	
(0,0,0,[
	(this_or_next|key_clicked,key_left_mouse_button),
	(key_clicked,key_space),
	],
	[
		(assign,"$g_can_rest",0),
		(rest_for_hours,0,0,0),
]),
	
	
(no_pause_mod_sensibility,0,0,[
	(eq,"$g_can_rest",0)],
	[
	(assign,"$g_can_rest",1),
]),
####no pause mod end###

(0.1,0,0,[],[ #sendind my position
	(set_fixed_point_multiplier, 1000),
	(party_get_position,pos1,"p_main_party"),
	(position_get_rotation_around_z,":rot",pos1),
	(position_get_x,":x",pos1),
	(position_get_y,":y",pos1),
	(call_script,"script_send_int_to_server",mpcamp_event_send_my_pos,3,":x",":y",":rot"),
]),

(0.2,0,0,[],[
	(call_script,"script_send_int_to_server",mpcamp_event_get_pos,0),
]),


(0,0,0,[],[
	(game_key_clicked,gk_mp_message_all),
	(start_presentation, "prsnt_chat_message"),
]),

(sending_receiving_frequency,0,0,[],[
	(call_script,"script_send_data"),
]),



 
]
