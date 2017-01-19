from header_common import *
from header_operations import *
from header_parties import *
from header_items import *
from header_skills import *
from header_triggers import *
from header_troops import *
from header_music import *

from module_constants import *

####################################################################################################################
# Simple triggers are the alternative to old style triggers. They do not preserve state, and thus simpler to maintain.
#
#  Each simple trigger contains the following fields:
# 1) Check interval: How frequently this trigger will be checked
# 2) Operation block: This must be a valid operation block. See header_operations.py for reference. 
####################################################################################################################



simple_triggers = [

# This trigger is deprecated. Use "script_game_event_party_encounter" in module_scripts.py instead  
  (ti_on_party_encounter,
   [
    ]),


# This trigger is deprecated. Use "script_game_event_simulate_battle" in module_scripts.py instead 
  (ti_simulate_battle,
   [
    ]),


  (1,
   [
      (try_begin),
        (eq, "$training_ground_position_changed", 0),
        (assign, "$training_ground_position_changed", 1),
		(set_fixed_point_multiplier, 100),
        (position_set_x, pos0, 7050),
        (position_set_y, pos0, 7200),
        (party_set_position, "p_training_ground_3", pos0),
      (try_end),
	  
      (gt,"$auto_besiege_town",0),
      (gt,"$g_player_besiege_town", 0),
      (ge, "$g_siege_method", 1),
      (store_current_hours, ":cur_hours"),
      (eq, "$g_siege_force_wait", 0),
      (ge, ":cur_hours", "$g_siege_method_finish_hours"),
      (neg|is_currently_night),
      (rest_for_hours, 0, 0, 0), #stop resting
    ]),


  (0,
   [
      (try_begin),
        (eq, "$bug_fix_version", 0),     
      
        #fix for hiding test_scene in older savegames
        (disable_party, "p_test_scene"),
        #fix for correcting town_1 siege type
        (party_set_slot, "p_town_1", slot_center_siege_with_belfry, 0),
        #fix for hiding player_faction notes
        (faction_set_note_available, "fac_player_faction", 0),
        #fix for hiding faction 0 notes
        (faction_set_note_available, "fac_no_faction", 0),
        #fix for removing kidnapped girl from party
        (try_begin),
          (neg|check_quest_active, "qst_kidnapped_girl"),
          (party_remove_members, "p_main_party", "trp_kidnapped_girl", 1),
        (try_end),
        #fix for not occupied but belong to a faction lords
        (try_for_range, ":cur_troop", lords_begin, lords_end),
          (try_begin),                
            (troop_slot_eq, ":cur_troop", slot_troop_occupation, slto_inactive),
            (store_troop_faction, ":cur_troop_faction", ":cur_troop"),
            (is_between, ":cur_troop_faction", "fac_kingdom_1", kingdoms_end),          
            (troop_set_slot, ":cur_troop", slot_troop_occupation, slto_kingdom_hero),          
          (try_end),
        (try_end),  
        #fix for an error in 1.105, also fills new slot values
        (call_script, "script_initialize_item_info"),  
        
        (assign, "$bug_fix_version", 1),     
      (try_end),  

      (eq,"$g_player_is_captive",1),
      (gt, "$capturer_party", 0),
      (party_is_active, "$capturer_party"),
      (party_relocate_near_party, "p_main_party", "$capturer_party", 0),
    ]),


#Auto-menu
  (0,
   [          
     (try_begin),
       (gt, "$g_last_rest_center", 0),
       (party_get_battle_opponent, ":besieger_party", "$g_last_rest_center"),
       (gt, ":besieger_party", 0),
       (store_faction_of_party, ":encountered_faction", "$g_last_rest_center"),
       (store_relation, ":faction_relation", ":encountered_faction", "fac_player_supporters_faction"),
       (store_faction_of_party, ":besieger_party_faction", ":besieger_party"),
       (store_relation, ":besieger_party_relation", ":besieger_party_faction", "fac_player_supporters_faction"),
       (ge, ":faction_relation", 0),
       (lt, ":besieger_party_relation", 0),
       (start_encounter, "$g_last_rest_center"),
       (rest_for_hours, 0, 0, 0), #stop resting
     (else_try),
       (store_current_hours, ":cur_hours"),
       (assign, ":check", 0),
       (try_begin),
         (neq, "$g_check_autos_at_hour", 0),
         (ge, ":cur_hours", "$g_check_autos_at_hour"),
         (assign, ":check", 1),
         (assign, "$g_check_autos_at_hour", 0),
       (try_end),
       (this_or_next|eq, ":check", 1),
       (map_free),
       (try_begin),
         (ge,"$auto_menu",1),
         (jump_to_menu,"$auto_menu"),
         (assign,"$auto_menu",-1),
       (else_try),
         (ge,"$auto_enter_town",1),
         (start_encounter, "$auto_enter_town"),
       (else_try),
         (ge,"$auto_besiege_town",1),
         (start_encounter, "$auto_besiege_town"),
       (else_try),
         (ge,"$g_camp_mode", 1),
         (assign, "$g_camp_mode", 0),
         (assign, "$g_infinite_camping", 0),
         (assign, "$g_player_icon_state", pis_normal),
         
         (rest_for_hours, 0, 0, 0), #stop camping
                  
         (display_message, "@Breaking camp..."),
       (try_end),
     (try_end),
     ]),



  #Music,
  (1,
   [
       (map_free),
       (call_script, "script_music_set_situation_with_culture", mtf_sit_travel),
	    ]),		
   
    
   
#Player raiding a village
# This trigger will check if player's raid has been completed and will lead control to village menu.
  (1,
   [
      (ge,"$g_player_raiding_village",1),
      (try_begin),
        (neq, "$g_player_is_captive", 0),
        #(rest_for_hours, 0, 0, 0), #stop resting - abort
        (assign,"$g_player_raiding_village",0),
      (else_try),
        (map_free), #we have been attacked during raid
        (assign,"$g_player_raiding_village",0),
      (else_try),
        (this_or_next|party_slot_eq, "$g_player_raiding_village", slot_village_state, svs_looted),
        (party_slot_eq, "$g_player_raiding_village", slot_village_state, svs_deserted),
        (start_encounter, "$g_player_raiding_village"),
        (rest_for_hours, 0),
        (assign,"$g_player_raiding_village",0),
        (assign,"$g_player_raid_complete",1),
      (else_try),
        (party_slot_eq, "$g_player_raiding_village", slot_village_state, svs_being_raided),
        (rest_for_hours, 3, 5, 1), #rest while attackable
      (else_try),
        (rest_for_hours, 0, 0, 0), #stop resting - abort
        (assign,"$g_player_raiding_village",0),
        (assign,"$g_player_raid_complete",0),
      (try_end),
    ]),

#  #Pay day.
#  (24 * 7,
#   [
#     (assign, "$g_presentation_lines_to_display_begin", 0),
#     (assign, "$g_presentation_lines_to_display_end", 15),
#     (assign, "$g_apply_budget_report_to_gold", 1),
#     (try_begin),
#       (eq, "$g_infinite_camping", 0),
#       (start_presentation, "prsnt_budget_report"),
#     (try_end),
#    ]),

  # Reducing luck by 1 in every 180 hours
  (180,
   [
     (val_sub, "$g_player_luck", 1),
     (val_max, "$g_player_luck", 0),
    ]),

	#reset time to spare
  (4,
   [
     (assign, "$g_time_to_spare", 1),

    (try_begin),
		(troop_slot_ge, "trp_player", slot_troop_spouse, active_npcs_begin),
		(assign, "$g_player_banner_granted", 1),
	(try_end),

	 ]),
  # Party Morale: Move morale towards target value.
  (24,
   [
      (call_script, "script_get_player_party_morale_values"),
      (assign, ":target_morale", reg0),
      (party_get_morale, ":cur_morale", "p_main_party"),
      (store_sub, ":dif", ":target_morale", ":cur_morale"),
      (store_div, ":dif_to_add", ":dif", 5),
      (store_mul, ":dif_to_add_correction", ":dif_to_add", 5),
      (try_begin),#finding ceiling of the value
        (neq, ":dif_to_add_correction", ":dif"),
        (try_begin),
          (gt, ":dif", 0),
          (val_add, ":dif_to_add", 1),
        (else_try),
          (val_sub, ":dif_to_add", 1),
        (try_end),
      (try_end),
      (val_add, ":cur_morale", ":dif_to_add"),
      (party_set_morale, "p_main_party", ":cur_morale"),      
    ]),
  

#Party AI: pruning some of the prisoners in each center (once a week)
  (24*7,
   [
       (try_for_range, ":center_no", centers_begin, centers_end),
         (party_get_num_prisoner_stacks, ":num_prisoner_stacks",":center_no"),
         (try_for_range_backwards, ":stack_no", 0, ":num_prisoner_stacks"),
           (party_prisoner_stack_get_troop_id, ":stack_troop",":center_no",":stack_no"),
           (neg|troop_is_hero, ":stack_troop"),
           (party_prisoner_stack_get_size, ":stack_size",":center_no",":stack_no"),
           (store_random_in_range, ":rand_no", 0, 40),
           (val_mul, ":stack_size", ":rand_no"),
           (val_div, ":stack_size", 100),
           (party_remove_prisoners, ":center_no", ":stack_troop", ":stack_size"),
         (try_end),
       (try_end),
    ]),

  #Adding net incomes to heroes (once a week)
  #Increasing debts to heroes by 1% (once a week)
  #Adding net incomes to centers (once a week)
  (24*7,
   [
       (try_for_range, ":troop_no", active_npcs_begin, active_npcs_end),
         (troop_get_slot, ":cur_debt", ":troop_no", slot_troop_player_debt),#Increasing debt
         (val_mul, ":cur_debt", 101),
         (val_div, ":cur_debt", 100),
         (troop_set_slot, ":troop_no", slot_troop_player_debt, ":cur_debt"),
         (call_script, "script_calculate_hero_weekly_net_income_and_add_to_wealth", ":troop_no"),#Adding net income
       (try_end),
	   
       (try_for_range, ":center_no", walled_centers_begin, walled_centers_end),
         #If non-player center, adding income to wealth
         (neg|party_slot_eq, ":center_no", slot_town_lord, "trp_player"), #center does not belong to player.
         (party_slot_ge, ":center_no", slot_town_lord, 1), #center belongs to someone.
         (party_get_slot, ":cur_wealth", ":center_no", slot_town_wealth),
         (party_get_slot, ":prosperity", ":center_no", slot_town_prosperity),
         (store_mul, ":added_wealth", ":prosperity", 15),
         (val_add, ":added_wealth", 700),
         (try_begin),
           (party_slot_eq, ":center_no", slot_party_type, spt_town),
           (val_mul, ":added_wealth", 3),
           (val_div, ":added_wealth", 2),
         (try_end),
         (val_add, ":cur_wealth", ":added_wealth"),
         (call_script, "script_calculate_weekly_party_wage", ":center_no"),
         (val_sub, ":cur_wealth", reg0),
         (val_max, ":cur_wealth", 0),
         (party_set_slot, ":center_no", slot_town_wealth, ":cur_wealth"),
       (try_end),
    ]),

  #Hiring men with hero wealths (once a day)
  #Hiring men with center wealths (once a day)
 
  # Process sieges
   (24,
   [
       (call_script, "script_process_sieges"),
    ]),

  # Process village raids
   (2,
   [
       (call_script, "script_process_village_raids"),
    ]),


  # Decide vassal ai
   (7,
    [
      (call_script, "script_init_ai_calculation"),
      #(call_script, "script_decide_kingdom_party_ais"),
      (try_for_range, ":troop_no", active_npcs_begin, active_npcs_end),
        (troop_slot_eq, ":troop_no", slot_troop_occupation, slto_kingdom_hero),
        (call_script, "script_calculate_troop_ai", ":troop_no"),
      (try_end),
      ]),

  # Refresh merchant inventories
   (168,
   [
      (try_for_range, ":village_no", villages_begin, villages_end),
        (call_script, "script_refresh_village_merchant_inventory", ":village_no"),
      (try_end),
    ]),

  #Refreshing village defenders
  #Clearing slot_village_player_can_not_steal_cattle flags
   (48,
   [
      (try_for_range, ":village_no", villages_begin, villages_end),
        (call_script, "script_refresh_village_defenders", ":village_no"),
        (party_set_slot, ":village_no", slot_village_player_can_not_steal_cattle, 0),
      (try_end),
    ]),

  # Refresh number of cattle in villages
  (24 * 7,
   [
     (try_for_range, ":village_no", centers_begin, centers_end),
	   (neg|is_between, ":village_no", castles_begin, castles_end),
	   (party_get_slot, ":num_cattle", ":village_no", slot_center_head_cattle),
	   (party_get_slot, ":num_sheep", ":village_no", slot_center_head_sheep),
	   (party_get_slot, ":num_acres", ":village_no", slot_center_acres_pasture),
	   (val_max, ":num_acres", 1),
	   
	   (store_mul, ":grazing_capacity", ":num_cattle", 400),
	   (store_mul, ":sheep_addition", ":num_sheep", 200),
	   (val_add, ":grazing_capacity", ":sheep_addition"),
	   (val_div, ":grazing_capacity", ":num_acres"),
	   
	   (store_random_in_range, ":random_no", 0, 100),
	   (try_begin), #Disaster
	     (eq, ":random_no", 0),#1% chance of epidemic - should happen once every two years
		 (val_min, ":num_cattle", 10),
		 
       (else_try), #Overgrazing
         (gt, ":grazing_capacity", 100),
		
         (val_mul, ":num_sheep", 90), #10% decrease at number of cattles
         (val_div, ":num_sheep", 100),
		
         (val_mul, ":num_cattle", 90), #10% decrease at number of sheeps
         (val_div, ":num_cattle", 100),
		 
       (else_try), #superb grazing
         (lt, ":grazing_capacity", 30),

         (val_mul, ":num_cattle", 120), #20% increase at number of cattles
         (val_div, ":num_cattle", 100),
         (val_add, ":num_cattle", 1),
		
         (val_mul, ":num_sheep", 120), #20% increase at number of sheeps
         (val_div, ":num_sheep", 100),
         (val_add, ":num_sheep", 1),
		
       (else_try), #very good grazing
         (lt, ":grazing_capacity", 60),

         (val_mul, ":num_cattle", 110), #10% increase at number of cattles
         (val_div, ":num_cattle", 100),
         (val_add, ":num_cattle", 1),
		
         (val_mul, ":num_sheep", 110), #10% increase at number of sheeps
         (val_div, ":num_sheep", 100),
         (val_add, ":num_sheep", 1),

       (else_try), #good grazing
         (lt, ":grazing_capacity", 100),
         (lt, ":random_no", 50),

         (val_mul, ":num_cattle", 105), #5% increase at number of cattles
         (val_div, ":num_cattle", 100),
         (try_begin), #if very low number of cattles and there is good grazing then increase number of cattles also by one
           (le, ":num_cattle", 20),
           (val_add, ":num_cattle", 1),
         (try_end),
		
         (val_mul, ":num_sheep", 105), #5% increase at number of sheeps
         (val_div, ":num_sheep", 100),
         (try_begin), #if very low number of sheeps and there is good grazing then increase number of sheeps also by one
           (le, ":num_sheep", 20),
           (val_add, ":num_sheep", 1),
         (try_end),		
       (try_end),

       (party_set_slot, ":village_no", slot_center_head_cattle, ":num_cattle"),
       (party_set_slot, ":village_no", slot_center_head_sheep, ":num_sheep"),	  	  	  
     (try_end),
    ]),

 
   (72,
   [
  # Updating trade good prices according to the productions
       (call_script, "script_update_trade_good_prices"),
 # Updating player odds
       (try_for_range, ":cur_center", centers_begin, centers_end),
         (party_get_slot, ":player_odds", ":cur_center", slot_town_player_odds),
         (try_begin),
           (gt, ":player_odds", 1000),
           (val_mul, ":player_odds", 95),
           (val_div, ":player_odds", 100),
           (val_max, ":player_odds", 1000),
         (else_try),
           (lt, ":player_odds", 1000),
           (val_mul, ":player_odds", 105),
           (val_div, ":player_odds", 100),
           (val_min, ":player_odds", 1000),
         (try_end),
         (party_set_slot, ":cur_center", slot_town_player_odds, ":player_odds"),
       (try_end),
    ]),


 #Increase castle food stores
  (2,
   [
       (try_for_range, ":center_no", castles_begin, castles_end),
         (party_slot_eq, ":center_no", slot_center_is_besieged_by, -1), #castle is not under siege
         (party_get_slot, ":center_food_store", ":center_no", slot_party_food_store),
         (val_add, ":center_food_store", 100),
         (call_script, "script_center_get_food_store_limit", ":center_no"),
         (assign, ":food_store_limit", reg0),
         (val_min, ":center_food_store", ":food_store_limit"),
         (party_set_slot, ":center_no", slot_party_food_store, ":center_food_store"),
       (try_end),
    ]),

 
  # Consuming food at every 14 hours
  (14,
   [
    (eq, "$g_player_is_captive", 0),
    (party_get_num_companion_stacks, ":num_stacks","p_main_party"),
    (assign, ":num_men", 0),
    (try_for_range, ":i_stack", 0, ":num_stacks"),
      (party_stack_get_size, ":stack_size","p_main_party",":i_stack"),
      (val_add, ":num_men", ":stack_size"),
    (try_end),
    (val_div, ":num_men", 3),
    (try_begin),
      (eq, ":num_men", 0),
      (val_add, ":num_men", 1),
    (try_end),
    
    (try_begin),
      (assign, ":number_of_foods_player_has", 0),
      (try_for_range, ":cur_edible", food_begin, food_end),      
        (call_script, "script_cf_player_has_item_without_modifier", ":cur_edible", imod_rotten),
        (val_add, ":number_of_foods_player_has", 1),
      (try_end),
      (try_begin),
        (ge, ":number_of_foods_player_has", 6),
        (unlock_achievement, ACHIEVEMENT_ABUNDANT_FEAST),        
      (try_end),
    (try_end),
    
    (assign, ":consumption_amount", ":num_men"),
    (assign, ":no_food_displayed", 0),
    (try_for_range, ":unused", 0, ":consumption_amount"),
      (assign, ":available_food", 0),
      (try_for_range, ":cur_food", food_begin, food_end),
        (item_set_slot, ":cur_food", slot_item_is_checked, 0),
        (call_script, "script_cf_player_has_item_without_modifier", ":cur_food", imod_rotten),
        (val_add, ":available_food", 1),
      (try_end),
      (try_begin),
        (gt, ":available_food", 0),
        (store_random_in_range, ":selected_food", 0, ":available_food"),
        (call_script, "script_consume_food", ":selected_food"),
      (else_try),
        (eq, ":no_food_displayed", 0),
        (display_message, "@Party has nothing to eat!", 0xFF0000),
        (call_script, "script_change_player_party_morale", -3),
        (assign, ":no_food_displayed", 1),
#NPC companion changes begin
        (try_begin),
            (call_script, "script_party_count_fit_regulars", "p_main_party"),
            (gt, reg0, 0),
            (call_script, "script_objectionable_action", tmt_egalitarian, "str_men_hungry"),
        (try_end),
#NPC companion changes end
      (try_end),
    (try_end),
    ]),

  # Setting item modifiers for food
  (24,
   [
     (troop_get_inventory_capacity, ":inv_size", "trp_player"),
     (try_for_range, ":i_slot", 0, ":inv_size"),
       (troop_get_inventory_slot, ":item_id", "trp_player", ":i_slot"),
       (this_or_next|eq, ":item_id", "itm_cattle_meat"),
       (this_or_next|eq, ":item_id", "itm_chicken"),
		(eq, ":item_id", "itm_pork"),
		
       (troop_get_inventory_slot_modifier, ":modifier", "trp_player", ":i_slot"),
       (try_begin),
         (ge, ":modifier", imod_fresh),
         (lt, ":modifier", imod_rotten),
         (val_add, ":modifier", 1),
         (troop_set_inventory_slot_modifier, "trp_player", ":i_slot", ":modifier"),
       (else_try),
         (lt, ":modifier", imod_fresh),
         (troop_set_inventory_slot_modifier, "trp_player", ":i_slot", imod_fresh),
       (try_end),
     (try_end),
    ]),

  # Updating player icon in every frame
  (0,
   [(troop_get_inventory_slot, ":cur_horse", "trp_player", 8), #horse slot
    (assign, ":new_icon", -1),
    (try_begin),
      (eq, "$g_player_icon_state", pis_normal),
      (try_begin),
        (ge, ":cur_horse", 0),
        (assign, ":new_icon", "icon_player_horseman"),
      (else_try),
        (assign, ":new_icon", "icon_player"),
      (try_end),
    (else_try),
      (eq, "$g_player_icon_state", pis_camping),
      (assign, ":new_icon", "icon_camp"),
    (else_try),
      (eq, "$g_player_icon_state", pis_ship),
      (assign, ":new_icon", "icon_ship"),
    (try_end),
    (neq, ":new_icon", "$g_player_party_icon"),
    (assign, "$g_player_party_icon", ":new_icon"),
    (party_set_icon, "p_main_party", ":new_icon"),
    ]),
  

  
  # Adding mercenary troops to the towns
  (72,
   [
     (call_script, "script_update_mercenary_units_of_towns"),
     #NPC changes begin
     # removes   (call_script, "script_update_companion_candidates_in_taverns"),
     #NPC changes end
     (call_script, "script_update_ransom_brokers"),
     (call_script, "script_update_tavern_travellers"),
     (call_script, "script_update_tavern_minstrels"),
     (call_script, "script_update_booksellers"),
     (call_script, "script_update_villages_infested_by_bandits"),
     (try_for_range, ":village_no", villages_begin, villages_end),
       (call_script, "script_update_volunteer_troops_in_village", ":village_no"),
       (call_script, "script_update_npc_volunteer_troops_in_village", ":village_no"),
     (try_end),
    ]),

  (24,
   [	
    (call_script, "script_update_other_taverngoers"),
	]),
	
  # Setting random walker types
  (36,
   [(try_for_range, ":center_no", centers_begin, centers_end),
      (this_or_next|party_slot_eq, ":center_no", slot_party_type, spt_town),
      (             party_slot_eq, ":center_no", slot_party_type, spt_village),
      (call_script, "script_center_remove_walker_type_from_walkers", ":center_no", walkert_needs_money),
      (call_script, "script_center_remove_walker_type_from_walkers", ":center_no", walkert_needs_money_helped),
      (store_random_in_range, ":rand", 0, 100),
      (try_begin),
        (lt, ":rand", 70),
        (neg|party_slot_ge, ":center_no", slot_town_prosperity, 60),
        (call_script, "script_cf_center_get_free_walker", ":center_no"),
        (call_script, "script_center_set_walker_to_type", ":center_no", reg0, walkert_needs_money),
      (try_end),
    (try_end),
    ]),

  # Checking center upgrades
  (12,
   [(try_for_range, ":center_no", centers_begin, centers_end),
      (party_get_slot, ":cur_improvement", ":center_no", slot_center_current_improvement),
      (gt, ":cur_improvement", 0),
      (party_get_slot, ":cur_improvement_end_time", ":center_no", slot_center_improvement_end_hour),
      (store_current_hours, ":cur_hours"),
      (ge, ":cur_hours", ":cur_improvement_end_time"),
      (party_set_slot, ":center_no", ":cur_improvement", 1),
      (party_set_slot, ":center_no", slot_center_current_improvement, 0),
      (call_script, "script_get_improvement_details", ":cur_improvement"),
      (try_begin),
        (party_slot_eq, ":center_no", slot_town_lord, "trp_player"),
        (str_store_party_name, s4, ":center_no"),
        (display_log_message, "@Building of {s0} in {s4} has been completed."),
      (try_end),
      (try_begin),
        (is_between, ":center_no", villages_begin, villages_end),
        (eq, ":cur_improvement", slot_center_has_fish_pond),
        (call_script, "script_change_center_prosperity", ":center_no", 5),
      (try_end),
    (try_end),
    ]),

  # Adding tournaments to towns
  # Adding bandits to towns and villages
  

  (3,
[
	(assign, "$g_player_tournament_placement", 0),
]),  
  
  # Taking denars from player while resting in not owned centers
  (1,
   [(neg|map_free),
    (is_currently_night),
#    (ge, "$g_last_rest_center", 0),
    (is_between, "$g_last_rest_center", centers_begin, centers_end),
    (neg|party_slot_eq, "$g_last_rest_center", slot_town_lord, "trp_player"),
    (store_faction_of_party, ":last_rest_center_faction", "$g_last_rest_center"),
    (neq, ":last_rest_center_faction", "fac_player_supporters_faction"),
    (store_current_hours, ":cur_hours"),
    (ge, ":cur_hours", "$g_last_rest_payment_until"),
    (store_add, "$g_last_rest_payment_until", ":cur_hours", 24),
    (store_troop_gold, ":gold", "trp_player"),
    (party_get_num_companions, ":num_men", "p_main_party"),
    (store_div, ":total_cost", ":num_men", 4),
    (val_add, ":total_cost", 1),
    (try_begin),
      (ge, ":gold", ":total_cost"),
      (display_message, "@You pay for accommodation."),
      (troop_remove_gold, "trp_player", ":total_cost"),
    (else_try),
      (gt, ":gold", 0),
      (troop_remove_gold, "trp_player", ":gold"),
    (try_end),
    ]),
    
  # Reduce renown slightly by 0.5% every week
  (7 * 24,
   [
       (troop_get_slot, ":player_renown", "trp_player", slot_troop_renown),
       (store_div, ":renown_decrease", ":player_renown", 200),
       (val_sub, ":player_renown", ":renown_decrease"),
       (troop_set_slot, "trp_player", slot_troop_renown, ":player_renown"),
    ]),

  # Read books if player is resting.
  (1, [(neg|map_free),
       (gt, "$g_player_reading_book", 0),
       (player_has_item, "$g_player_reading_book"),
       (store_attribute_level, ":int", "trp_player", ca_intelligence),
       (item_get_slot, ":int_req", "$g_player_reading_book", slot_item_intelligence_requirement),
       (le, ":int_req", ":int"),
       (item_get_slot, ":book_reading_progress", "$g_player_reading_book", slot_item_book_reading_progress),
       (item_get_slot, ":book_read", "$g_player_reading_book", slot_item_book_read),
       (eq, ":book_read", 0),
       (val_add, ":book_reading_progress", 7),
       (item_set_slot, "$g_player_reading_book", slot_item_book_reading_progress, ":book_reading_progress"),
       (ge, ":book_reading_progress", 1000),
       (item_set_slot, "$g_player_reading_book", slot_item_book_read, 1),
       (str_store_item_name, s1, "$g_player_reading_book"),
       (str_clear, s2),
       (try_begin),
         (eq, "$g_player_reading_book", "itm_book_tactics"),
         (troop_raise_skill, "trp_player", "skl_tactics", 1),
         (str_store_string, s2, "@ Your tactics skill has increased by 1."),
       (else_try),
         (eq, "$g_player_reading_book", "itm_book_persuasion"),
         (troop_raise_skill, "trp_player", "skl_persuasion", 1),
         (str_store_string, s2, "@ Your persuasion skill has increased by 1."),
       (else_try),
         (eq, "$g_player_reading_book", "itm_book_leadership"),
         (troop_raise_skill, "trp_player", "skl_leadership", 1),
         (str_store_string, s2, "@ Your leadership skill has increased by 1."),
       (else_try),
         (eq, "$g_player_reading_book", "itm_book_intelligence"),
         (troop_raise_attribute, "trp_player", ca_intelligence, 1),
         (str_store_string, s2, "@ Your intelligence has increased by 1."),
       (else_try),
         (eq, "$g_player_reading_book", "itm_book_trade"),
         (troop_raise_skill, "trp_player", "skl_trade", 1),
         (str_store_string, s2, "@ Your trade skill has increased by 1."),
       (else_try),
         (eq, "$g_player_reading_book", "itm_book_weapon_mastery"),
         (troop_raise_skill, "trp_player", "skl_weapon_master", 1),
         (str_store_string, s2, "@ Your weapon master skill has increased by 1."),
       (else_try),
         (eq, "$g_player_reading_book", "itm_book_engineering"),
         (troop_raise_skill, "trp_player", "skl_engineer", 1),
         (str_store_string, s2, "@ Your engineer skill has increased by 1."),
       (try_end),
       
       (unlock_achievement, ACHIEVEMENT_BOOK_WORM),

       (try_begin),
         (eq, "$g_infinite_camping", 0),
         (dialog_box, "@You have finished reading {s1}.{s2}", "@Book Read"),
       (try_end),  
              
       (assign, "$g_player_reading_book", 0),	   	   
       ]),

# Removing cattle herds if they are way out of range
  (12, [(try_for_parties, ":cur_party"),
          (party_slot_eq, ":cur_party", slot_party_type, spt_cattle_herd),
          (store_distance_to_party_from_party, ":dist",":cur_party", "p_main_party"),
          (try_begin),
            (gt, ":dist", 30),
            (remove_party, ":cur_party"),
            (try_begin),
              #Fail quest if the party is the quest party
              (check_quest_active, "qst_move_cattle_herd"),
              (neg|check_quest_concluded, "qst_move_cattle_herd"),
              (quest_slot_eq, "qst_move_cattle_herd", slot_quest_target_party, ":cur_party"),
              (call_script, "script_fail_quest", "qst_move_cattle_herd"),
            (end_try),
          (else_try),
            (gt, ":dist", 10),
            (party_set_slot, ":cur_party", slot_cattle_driven_by_player, 0),
            (party_set_ai_behavior, ":cur_party", ai_bhvr_hold),
          (try_end),
        (try_end),
    ]),

  
#####!!!!!

# Village upgrade triggers

# School
  (30 * 24,
   [(try_for_range, ":cur_village", villages_begin, villages_end),
      (party_slot_eq, ":cur_village", slot_town_lord, "trp_player"),
      (party_slot_eq, ":cur_village", slot_center_has_school, 1),
      (party_get_slot, ":cur_relation", ":cur_village", slot_center_player_relation),
      (val_add, ":cur_relation", 1),
      (val_min, ":cur_relation", 100),
      (party_set_slot, ":cur_village", slot_center_player_relation, ":cur_relation"),
    (try_end),
    ]),

# Quest triggers:

# Remaining days text update
  (24, [(try_for_range, ":cur_quest", all_quests_begin, all_quests_end),
          (try_begin),
            (check_quest_active, ":cur_quest"),
            (try_begin),
              (neg|check_quest_concluded, ":cur_quest"),
              (quest_slot_ge, ":cur_quest", slot_quest_expiration_days, 1),
              (quest_get_slot, ":exp_days", ":cur_quest", slot_quest_expiration_days),
              (val_sub, ":exp_days", 1),
              (try_begin),
                (eq, ":exp_days", 0),
                (call_script, "script_abort_quest", ":cur_quest", 1),
              (else_try),
                (quest_set_slot, ":cur_quest", slot_quest_expiration_days, ":exp_days"),
                (assign, reg0, ":exp_days"),
                (add_quest_note_from_sreg, ":cur_quest", 7, "@You have {reg0} days to finish this quest.", 0),
              (try_end),
            (try_end),
          (else_try),
            (quest_slot_ge, ":cur_quest", slot_quest_dont_give_again_remaining_days, 1),
            (quest_get_slot, ":value", ":cur_quest", slot_quest_dont_give_again_remaining_days),
            (val_sub, ":value", 1),
            (quest_set_slot, ":cur_quest", slot_quest_dont_give_again_remaining_days, ":value"),
          (try_end),
        (try_end),
    ]),


# Move cattle herd
  (0.5, [(check_quest_active,"qst_move_cattle_herd"),
         (neg|check_quest_concluded,"qst_move_cattle_herd"),
         (quest_get_slot, ":target_party", "qst_move_cattle_herd", slot_quest_target_party),
         (quest_get_slot, ":target_center", "qst_move_cattle_herd", slot_quest_target_center),
         (store_distance_to_party_from_party, ":dist",":target_party", ":target_center"),
         (lt, ":dist", 3),
         (remove_party, ":target_party"),
         (call_script, "script_succeed_quest", "qst_move_cattle_herd"),
    ]),

  (2, [
       (try_for_range, ":troop_no", active_npcs_begin, active_npcs_end),
		 (troop_slot_eq, ":troop_no", slot_troop_occupation, slto_kingdom_hero),
		 (troop_get_slot, ":party_no", ":troop_no", slot_troop_leaded_party),
         (ge, ":party_no", 1),
		 (party_is_active, ":party_no"),
         (party_slot_eq, ":party_no", slot_party_following_player, 1),
         (store_current_hours, ":cur_time"),
         (neg|party_slot_ge, ":party_no", slot_party_follow_player_until_time, ":cur_time"),
         (party_set_slot, ":party_no", slot_party_commander_party, -1),
         (party_set_slot, ":party_no", slot_party_following_player, 0),
         (assign,  ":dont_follow_period", 200),
         (store_add, ":dont_follow_time", ":cur_time", ":dont_follow_period"),
         (party_set_slot, ":party_no", slot_party_dont_follow_player_until_time,  ":dont_follow_time"),
       (try_end),
    ]),

  (1,
   [
     (call_script, "script_calculate_castle_prosperities_by_using_its_villages"),

     (store_add, ":fac_kingdom_6_plus_one", "fac_kingdom_6", 1),

     (try_for_range, ":faction_1", "fac_kingdom_1", ":fac_kingdom_6_plus_one"),
       (try_for_range, ":faction_2", "fac_kingdom_1", ":fac_kingdom_6_plus_one"),
         (store_relation, ":faction_relation", ":faction_1", ":faction_2"),
         (str_store_faction_name, s7, ":faction_1"),
         (str_store_faction_name, s8, ":faction_2"),
         (neq, ":faction_1", ":faction_2"),
         (assign, reg1, ":faction_relation"),
         #(display_message, "@{s7}-{s8}, relation is {reg1}"),
       (try_end),
     (try_end),          
   ]),
   
  (1,
   [   
     (try_begin),
       (eq, "$g_player_is_captive", 1),
       (neg|party_is_active, "$capturer_party"),
       (rest_for_hours, 0, 0, 0),
     (try_end),            
     
     (assign, ":village_no", "$next_center_will_be_fired"),
     (party_get_slot, ":is_there_already_fire", ":village_no", slot_village_smoke_added),
     (eq, ":is_there_already_fire", 0),
	 
	 
     (try_begin),
       (party_get_slot, ":bound_center", ":village_no", slot_village_bound_center),  
       (party_get_slot, ":last_nearby_fire_time", ":bound_center", slot_town_last_nearby_fire_time),
       (store_current_hours, ":cur_hours"),
	   
	   (try_begin),
		(eq, "$cheat_mode", 1),
		(is_between, ":village_no", centers_begin, centers_end),
		(is_between, ":bound_center", centers_begin, centers_end),
		(str_store_party_name, s4, ":village_no"),
		(str_store_party_name, s5, ":bound_center"),
		(store_current_hours, reg3),
        (party_get_slot, reg4, ":bound_center", slot_town_last_nearby_fire_time),
		(display_message, "@{!}DEBUG - Checking fire at {s4} for {s5} - current time {reg3}, last nearby fire {reg4}"),
	   (try_end),
	   
	   
       (eq, ":cur_hours", ":last_nearby_fire_time"),
       (party_add_particle_system, ":village_no", "psys_map_village_fire"),
       (party_add_particle_system, ":village_no", "psys_map_village_fire_smoke"),       
     (else_try),  
       (store_add, ":last_nearby_fire_finish_time", ":last_nearby_fire_time", fire_duration),
       (eq, ":last_nearby_fire_finish_time", ":cur_hours"),
       (party_clear_particle_systems, ":village_no"),
     (try_end),  
     

   ]),
   
  
  (24,
   [
	  # Setting food bonuses in every 6 hours again and again because of a bug (we could not find its reason) which decreases especially slot_item_food_bonus slots of items to 0.
	  #Staples
      (item_set_slot, "itm_bread", slot_item_food_bonus, 8), #brought up from 4
      (item_set_slot, "itm_grain", slot_item_food_bonus, 2), #new - can be boiled as porridge
	  
	  #Fat sources - preserved
      (item_set_slot, "itm_smoked_fish", slot_item_food_bonus, 4),
      (item_set_slot, "itm_dried_meat", slot_item_food_bonus, 5),
      (item_set_slot, "itm_cheese", slot_item_food_bonus, 5),
      (item_set_slot, "itm_sausages", slot_item_food_bonus, 5),
      (item_set_slot, "itm_butter", slot_item_food_bonus, 4), #brought down from 8

	  #Fat sources - perishable
      (item_set_slot, "itm_chicken", slot_item_food_bonus, 8), #brought up from 7
      (item_set_slot, "itm_cattle_meat", slot_item_food_bonus, 7), #brought down from 7
      (item_set_slot, "itm_pork", slot_item_food_bonus, 6), #brought down from 6
	  
	  #Produce
      (item_set_slot, "itm_raw_olives", slot_item_food_bonus, 1),
      (item_set_slot, "itm_cabbages", slot_item_food_bonus, 2),
      (item_set_slot, "itm_raw_grapes", slot_item_food_bonus, 3),
      (item_set_slot, "itm_apples", slot_item_food_bonus, 4), #brought down from 5

	  #Sweet items
      (item_set_slot, "itm_raw_date_fruit", slot_item_food_bonus, 4), #brought down from 8
      (item_set_slot, "itm_honey", slot_item_food_bonus, 6), #brought down from 12
      
      (item_set_slot, "itm_wine", slot_item_food_bonus, 5),
      (item_set_slot, "itm_ale", slot_item_food_bonus, 4),
   ]),
  (24,
   []),
  (24,
   []),
  (24,
   []),
  (24,
   []),
  (24,
   []),
  (24,
   []),
  (24,
   []),
  (24,
   []),
  (24,
   []),
]
