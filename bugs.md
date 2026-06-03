# Bugs: `npd_management`

- I succesfully created the npd item NPD-MP-00011
- I created the nutritional profile for the npd item NPD-MP-00011, but forgot to check "is_default" and submitetd it. 
    - I think that there should be a logic in which "is_default" should be set as 1 as default for new nutritional profiles. 
    - Additionally this field should be allowed to modify after submit and Once a nutritional profile is set as default and submitted/updated, the "is_default" field of all other nutritional profiles for the same npd_item/item should be set to 0.
- I created NPD-MP-00009 and NPD-MP-00010 and created nutritional profiles for them. then created a nutritional profile for each and manually set "is default" as true and submitted/updated.
  - When I promoted both items (each at a time) only the Item created from NPD-MP-00010 (MP-00010) replicated a new nutritional profile based on it predecesor nutritional profile. the one created from NPD-MP-00009 (MP-00009) did not replicate the nutritional profile.



- I created an NPD BOM from 3 NPD items (all of which I had previously promoted) and then tried to promote the NPD-BOM but got the error "AttributeError: 'NPDBOM' object has no attribute 'is_promoted'"