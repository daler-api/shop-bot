from aiogram.fsm.state import StatesGroup, State


class FindItem(StatesGroup):
    brand = State()
    category = State()
    sub_category = State()

    not_found_item = State()
    item = State()

    purchase = State()
    input_name = State()
    input_phone = State()

    select_delivery = State()
    sdek_pickup_point = State()
    input_address = State()

    input_comment = State()

    place_order = State()

    item_out_stock = State()
    size_out_stock = State()

    favorite = State()


class CategoryEdit(StatesGroup):
    brand = State()
    category = State()
    sub_category = State()

    add_new_brand = State()
    add_new_category = State()
    add_new_sub_category = State()

    edit_brand = State()
    edit_category = State()
    edit_sub_category = State()

    edit_name_brand = State()
    edit_name_category = State()
    edit_name_sub_category = State()


class ItemActs(StatesGroup):
    brand = State()
    category = State()
    sub_category = State()

    items = State()

    not_found_items = State()
    item = State()

    availability = State()
    price = State()
    photo = State()
    name = State()
    desc = State()
    link = State()

    new_item_name = State()
    new_item_desc = State()
    new_item_photo = State()
    new_item_availability = State()
    new_item_price = State()
    new_item_link = State()


class Search(StatesGroup):
    purchase = State()
    input_name = State()
    input_phone = State()

    select_delivery = State()
    sdek_pickup_point = State()
    input_address = State()

    input_comment = State()

    place_order = State()

    item_out_stock = State()
    size_out_stock = State()

    favorite = State()
