def make_substance_dict(limit_lenght=250):
    subs_dict = OrderedDict()
    for subst in substance_list:
        subst = subst.lower()
        nest_dict = OrderedDict()
        tw_length = 0
        for info_ in post_infos_de:

            if type(substance_dic[subst][info_]) == str:
                text_out = replace_emojis_unicode(str(substance_dic[subst][info_]))
            else:
                text_out = ast.literal_eval(
                    replace_emojis_unicode(str(substance_dic[subst][info_])))

            if info_ in tittles_list:
                text_out = f"{info_}:\n {text_out}"
            elif info_ == "VIVID Safer-Use Tipps":
                text_out = f"Safer-Use Tipps:\n {text_out}"

            if info_ in ["dose_dict", "wirkdauer_dict"]:

                if len(text_out) <= limit_lenght:
                    text_out = tabulate(pd.DataFrame.from_dict(text_out), tablefmt="pretty")
                    nest_dict[info_] = text_out
                    tw_length += 1

            elif len(text_out) >= limit_lenght:

                for i, trunc_txt in enumerate(smart_truncate(text_out)):
                    tw_length += 1
                    nest_dict[f"{info_}_{i}"] = trunc_txt

            else:
                nest_dict[info_] = text_out
                tw_length += 1

            subs_dict[subst] = nest_dict
            subs_dict[subst]["tw_length"] = tw_length
    return subs_dict
    
    
