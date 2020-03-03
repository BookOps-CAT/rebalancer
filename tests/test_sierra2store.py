from datetime import date


from context import sierra2store


def test_parse_ids_positive():
    assert sierra2store.prep_ids('b218000297') == 21800029
    assert sierra2store.prep_ids('i371027913') == 37102791


def test_parse_ids_when_id_is_none():
    assert sierra2store.prep_ids(None) is None


def test_pares_ids_when_id_is_string():
    assert sierra2store.prep_ids('some string') is None


def test_prep_title():
    assert sierra2store.prep_title(
        '880-01 Bozhii pristani : rasskazy palomnikov.') == 'Bozhii pristani : rasskazy palomnikov.'
    assert sierra2store.prep_title(
        'Los cimientos del cielo / Juan Miguel Zunzunegui.') == 'Los cimientos del cielo'
    assert sierra2store.prep_title(
        '880-02 Tie xue zhan jiang / Zhuqian.') == 'Tie xue zhan jiang'


def test_prep_title_long():
    assert len(sierra2store.prep_title(
        'Test title' * 200)) == 200


def test_prep_author():
    assert sierra2store.prep_author(
        '880-01 Backman, Fredrik, 1981- author.') == 'Backman, Fredrik, 1981-'
    assert sierra2store.prep_author(
        '880-01 Zhuqian.') == 'Zhuqian'
    assert sierra2store.prep_author(
        'Keai.') == 'Keai'
    assert sierra2store.prep_author(
        'Denning, G. S. (Gabriel), author.') == 'Denning, G. S. (Gabriel)'
    assert sierra2store.prep_author(
        'Leon, Donna, author.') == 'Leon, Donna'
    assert sierra2store.prep_author(
        'Higashimura, Akiko, author, artist.') == 'Higashimura, Akiko'
    assert sierra2store.prep_author(
        'Krosoczka, Jarrett, author, illustrator.') == 'Krosoczka, Jarrett'


def test_prep_author_empty_string():
    assert sierra2store.prep_author(
        '') is None


def test_prep_author_long():
    assert len(sierra2store.prep_author(
        'Author' * 150)) == 150


def test_parse_pub_date_positive():
    assert sierra2store.parse_pub_date(
        'New York : Thomas Dunne Books, 2017.') == '2017'
    assert sierra2store.parse_pub_date(
        'New York : New York University, [2018]') == '2018'
    assert sierra2store.parse_pub_date(
        'Indianapolis, Indiana : John Wiley & Sons, Inc., [2017]"~"©2018"') == '2017'


def test_parse_pub_date_failed():
    assert sierra2store.parse_pub_date(
        'Wyandanch, NY : Urban Books') is None


def test_parse_pub_date_when_pub_info_is_none():
    assert sierra2store.parse_pub_date(
        None) is None


def test_string2date_positive():
    assert sierra2store.string2date(
        '03-02-2019 11:37') == date.fromisoformat('2019-03-02')


def test_string2date_when_date_str_is_none():
    assert sierra2store.string2date(
        None) is None


def test_string2date_when_date_str_invalid():
    assert sierra2store.string2date(
        '2019-03-02') is None


def test_get_audn_id():
    audn_idx = {
        None: 1,
        'a': 2,
        'j': 3,
        'y': 4}
    assert sierra2store.get_audience_id(
        'vca0n', audn_idx) == 2
    assert sierra2store.get_audience_id(
        'saj0y', audn_idx) == 3
    assert sierra2store.get_audience_id(
        'mpy0n', audn_idx) == 4
    assert sierra2store.get_audience_id(
        'mm3an', audn_idx) == 1  # is this a correct behavior? should we combine adult and unknown?


def test_get_audn_id_when_empty_string():
    audn_idx = {None: 1}
    assert sierra2store.get_audience_id(
        '', audn_idx) == 1


def test_get_language_id():
    lang_idx = {
        None: 1,
        'ara': 2,
        'chi': 4,
        'eng': 5,
        'spa': 19
    }
    assert sierra2store.get_language_id(
        'J-Spa 630.78 R', lang_idx) == 19
    assert sierra2store.get_language_id(
        'J PIC ANDERSON', lang_idx) == 5
    assert sierra2store.get_language_id(
        'SPA GRAPHIC GN FIC KISHIMOTO', lang_idx) == 19
    assert sierra2store.get_language_id(
        'CHI FIC GALBRAITH', lang_idx) == 4
    assert sierra2store.get_language_id(
        'ARA J-E ADAMS', lang_idx) == 2


def test_get_itemtype_id():
    itemtype_idx = {
        0: 46,
        101: 101,
    }
    assert sierra2store.get_itemtype_id(
        '101', itemtype_idx) == 101
    assert sierra2store.get_itemtype_id(
        101, itemtype_idx) == 101
    assert sierra2store.get_itemtype_id(
        '5', itemtype_idx) == 46


def test_string2int():
    assert sierra2store.string2int(
        '2') == 2
    assert sierra2store.string2int(
        2) == 2
    assert sierra2store.string2int(
        'a') == 0


def test_determine_nyp_mat_cat_for_general_fiction():
    assert sierra2store.determine_nyp_mat_cat(
        'CHI FIC JIQIU') == 'fi'
    assert sierra2store.determine_nyp_mat_cat(
        'FIC ALCOTT') == 'fi'
    assert sierra2store.determine_nyp_mat_cat(
        'FIC C') == 'fi'
    assert sierra2store.determine_nyp_mat_cat(
        'HAT FIC JEAN PIERRE') == 'fi'
    assert sierra2store.determine_nyp_mat_cat(
        'J FIC ANDRI SNAER MAGNASON') == 'fi'
    assert sierra2store.determine_nyp_mat_cat(
        'J READALONG FIC BERNSTROM') == 'fi'


def test_determine_nyp_mat_cat_for_classics():
    assert sierra2store.determine_nyp_mat_cat(
        'CLASSICS FIC BRADBURY') == 'cl'


def test_determine_nyp_mat_cat_for_graphic_novels():
    assert sierra2store.determine_nyp_mat_cat(
        'GN FIC SHULZ') == 'gn'
    assert sierra2store.determine_nyp_mat_cat(
        'GRAPHIC GN FIC DHALIWAL') == 'gn'
    assert sierra2store.determine_nyp_mat_cat(
        'GRAPHIC GN FIC C') == 'gn'
    assert sierra2store.determine_nyp_mat_cat(
        'JPN GRAPHIC GN FIC OTOMO') == 'gn'
    assert sierra2store.determine_nyp_mat_cat(
        'Spa GN FIC L') == 'gn'
    assert sierra2store.determine_nyp_mat_cat(
        'J GRAPHIC GN FIC HOLM') == 'gn'


def test_determine_nyp_mat_cat_for_biography():
    assert sierra2store.determine_nyp_mat_cat(
        'GRAPHIC B DAHMER D') == 'bi'
    assert sierra2store.determine_nyp_mat_cat(
        'FRE B BUFFET PICABIA B') == 'bi'
    assert sierra2store.determine_nyp_mat_cat(
        'RUS B VOLCHEK R') == 'bi'
    assert sierra2store.determine_nyp_mat_cat(
        'B FRANCIS M') == 'bi'
    assert sierra2store.determine_nyp_mat_cat(
        'J B Adams M') == 'bi'


def test_determine_nyp_mat_cat_for_large_print():
    assert sierra2store.determine_nyp_mat_cat(
        'LG PRINT 362.14 B') == 'lp'
    assert sierra2store.determine_nyp_mat_cat(
        'LG PRINT B CHARLES S') == 'lp'
    assert sierra2store.determine_nyp_mat_cat(
        'LG PRINT FIC CUSSLER') == 'lp'
    assert sierra2store.determine_nyp_mat_cat(
        'LG PRINT SCI FI ABRAHAM') == 'lp'
    assert sierra2store.determine_nyp_mat_cat(
        'LG-PRINT FIC BRADBURY') == 'lp'
    assert sierra2store.determine_nyp_mat_cat(
        'LG-PRINT MYSTERY CANADEO') == 'lp'
    assert sierra2store.determine_nyp_mat_cat(
        'J LG PRINT FIC APPLEGATE') == 'lp'


def test_determine_nyp_mat_cat_for_mystery():
    assert sierra2store.determine_nyp_mat_cat(
        'MYSTERY ADAMS') == 'my'


def test_determine_nyp_mat_cat_for_romance():
    assert sierra2store.determine_nyp_mat_cat(
        'ROMANCE B') == 'rm'
    assert sierra2store.determine_nyp_mat_cat(
        'ROMANCE AUSTIN') == 'rm'


def test_determine_nyp_mat_cat_for_science_fiction():
    assert sierra2store.determine_nyp_mat_cat(
        'SCI FI COREY') == 'sf'


def test_determine_nyp_mat_cat_for_urban_fiction():
    assert sierra2store.determine_nyp_mat_cat(
        'URBAN ARMSTEAD') == 'ur'
    assert sierra2store.determine_nyp_mat_cat(
        'URBAN B') == 'ur'


def test_determine_nyp_mat_cat_for_westerns():
    assert sierra2store.determine_nyp_mat_cat(
        'WESTERN BRYANT') == 'we'


def test_determine_nyp_mat_cat_for_dewey_0xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 080.9 D') == 'd0'
    assert sierra2store.determine_nyp_mat_cat(
        '005.1 G') == 'd0'
    assert sierra2store.determine_nyp_mat_cat(
        'J 005.1 S') == 'd0'


def test_determine_nyp_mat_cat_for_dewey_1xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 153.42 M') == 'd1'


def test_determine_nyp_mat_cat_for_dewey_2xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 299.792 RUIZ, MIGUE') == 'd2'


def test_determine_nyp_mat_cat_for_dewey_3xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 345.07 K') == 'd3'


def test_determine_nyp_mat_cat_for_dewey_4xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 428.5 BONK, N A') == 'd4'


def test_determine_nyp_mat_cat_for_dewey_5xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 508.4955 DURRELL, GE') == 'd5'
    assert sierra2store.determine_nyp_mat_cat(
        'J READALONG 597.95 S') == 'd5'


def test_determine_nyp_mat_cat_for_dewey_6xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 616.8 S') == 'd6'
    assert sierra2store.determine_nyp_mat_cat(
        'J 641.51 S') == 'd6'


def test_determine_nyp_mat_cat_for_dewey_7xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 782.85 O') == 'd7'


def test_determine_nyp_mat_cat_for_dewey_8xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 818 SAROYAN, WI') == 'd8'
    assert sierra2store.determine_nyp_mat_cat(
        '811 Forman') == 'd8'
    assert sierra2store.determine_nyp_mat_cat(
        '818 HUGHES R~"pjl CATBL"') == 'd8'
    assert sierra2store.determine_nyp_mat_cat(
        '822.33-H P') == 'd8'


def test_determine_nyp_mat_cat_for_dewey_9xx():
    assert sierra2store.determine_nyp_mat_cat(
        'RUS 943.086 S') == 'd9'


def test_determine_nyp_mat_cat_for_non_fic_in_graphic_format():
    assert sierra2store.determine_nyp_mat_cat(
        'GRAPHIC 817 PATTERSON') == 'd8'
    assert sierra2store.determine_nyp_mat_cat(
        'GRAPHIC 306.768 KAYE') == 'd3'
    assert sierra2store.determine_nyp_mat_cat(
        'J GRAPHIC 560.17 H') == 'd5'


def test_determine_nyp_mat_cat_for_easy_reader():
    assert sierra2store.determine_nyp_mat_cat(
        'J E B') == 'er'
    assert sierra2store.determine_nyp_mat_cat(
        'J E CARLE') == 'er'


def test_determine_nyp_mat_cat_for_picture_books():
    assert sierra2store.determine_nyp_mat_cat(
        'J FRE PIC ANTONY') == 'pi'
    assert sierra2store.determine_nyp_mat_cat(
        'J PIC A') == 'pi'


def test_determine_nyp_mat_cat_for_holiday_books():
    assert sierra2store.determine_nyp_mat_cat(
        'J HOLIDAY PIC B') == 'ho'


def test_determine_nyp_mat_cat_for_young_reader():
    assert sierra2store.determine_nyp_mat_cat(
        'J YR FIC A') == 'yr'


def test_determine_nyp_mat_cat_for_dvds():
    assert sierra2store.determine_nyp_mat_cat(
        'J FRE DVD TV ATCHOUM') == 'dv'


def test_determine_nyp_mat_cat_for_undefined():
    assert sierra2store.determine_nyp_mat_cat(
        'PER') is None
    assert sierra2store.determine_nyp_mat_cat(
        'J PER') is None


def test_determine_bpl_mat_cat_for_empty_call_no_string():
    assert sierra2store.determine_bpl_mat_cat(
        '', '87awl', '-') is None


def test_determine_bpl_mat_cat_when_no_shelf_code():
    assert sierra2store.determine_bpl_mat_cat(
        'J 641.815 K', '03', 'u') == 'gn'
    assert sierra2store.determine_bpl_mat_cat(
        'FIC ADAMS', '41', '-') == 'fi'
    assert sierra2store.determine_bpl_mat_cat(
        'FIC ADAMS', '41', 's') == 'sf'
    assert sierra2store.determine_bpl_mat_cat(
        'B ADAMS C', '41', '-') == 'bi'
    assert sierra2store.determine_bpl_mat_cat(
        'J-E ADAMS', '02', '-') == 'pi'
    assert sierra2store.determine_bpl_mat_cat(
        'SPA FIC ADAMS', '41', '-') == 'fi'


def test_determine_bpl_mat_cat_for_general_fiction():
    assert sierra2store.determine_bpl_mat_cat(
        'FIC ADAMS', '14afc', '-') == 'fi'
    assert sierra2store.determine_bpl_mat_cat(
        'POL FIC ADAMS', '41awl', '-') == 'fi'
    assert sierra2store.determine_bpl_mat_cat(
        'RUS J FIC LAGIN', '41awl', '-') == 'fi'


def test_determine_bpl_mat_cat_for_short_stories():
    assert sierra2store.determine_bpl_mat_cat(
        'FIC WURZBACHER', '47ash', 'y') == 'st'

    # short stories treated as general ficiton
    assert sierra2store.determine_bpl_mat_cat(
        'FIC C', '87afc', 'y') == 'st'


def test_determine_bpl_mat_cat_for_science_fiction():
    assert sierra2store.determine_bpl_mat_cat(
        'FIC COREY', '14asf', 's') == 'sf'
    # deck book
    assert sierra2store.determine_bpl_mat_cat(
        'FIC ASIMOV', '14adk', 's') == 'sf'


def test_determine_bpl_mat_cat_for_mystery():
    assert sierra2store.determine_bpl_mat_cat(
        'FIC MACRAE', '42afc', 'm') == 'my'
    assert sierra2store.determine_bpl_mat_cat(
        'FIC MACRAE', '42amy', 'm') == 'my'


def test_determine_bpl_mat_cat_for_bridge_books():
    assert sierra2store.determine_bpl_mat_cat(
        'J FIC COVEN', '45jfc', 'k') == 'yr'


def test_determine_bpl_mat_cat_for_graphic_novel():
    assert sierra2store.determine_bpl_mat_cat(
        'J FIC STILTON', '45jfc', 'u') == 'gn'
    assert sierra2store.determine_bpl_mat_cat(
        'FIC PANETTA', '03yfc', 'u') == 'gn'

    assert sierra2store.determine_bpl_mat_cat(
        'J 641.815 K', '03', 'u') == 'gn'


def test_determine_bpl_mat_cat_for_romances():
    assert sierra2store.determine_bpl_mat_cat(
        'FIC CHAPMAN', '14apb', 'n') == 'rm'


def test_determine_bpl_mat_cat_for_large_print():
    assert sierra2store.determine_bpl_mat_cat(
        'FIC CARCATERRA', '90alp', 'l') == 'lp'
    assert sierra2store.determine_bpl_mat_cat(
        '306.362 W', '90alp', 'l') == 'lp'
    assert sierra2store.determine_bpl_mat_cat(
        'B MOORE M', '90alp', 'l') == 'lp'


def test_determine_bpl_mat_cat_for_biography():
    assert sierra2store.determine_bpl_mat_cat(
        'J B PAYNE C', '62jbi', '-') == 'bi'
    assert sierra2store.determine_bpl_mat_cat(
        'B BROWN B', '62abi', '-') == 'bi'
    assert sierra2store.determine_bpl_mat_cat(
        'RUS B GUBERMAN G', '42awl', '-') == 'bi'


def test_determine_bpl_mat_cat_for_picture_books():
    assert sierra2store.determine_bpl_mat_cat(
        'SPA J-E GALAN', '41jwl', '-') == 'pi'
    assert sierra2store.determine_bpl_mat_cat(
        'POL J-E', '41jwl', '-') == 'pi'
    assert sierra2store.determine_bpl_mat_cat(
        'J-E', '02jje', '-') == 'pi'
    assert sierra2store.determine_bpl_mat_cat(
        'J-E SCIESZKA', '02jje', '-') == 'pi'


def test_determine_bpl_mat_cat_for_early_readers():
    assert sierra2store.determine_bpl_mat_cat(
        'J-E SCIESZKA', '02jer', '-') == 'er'


def test_determine_bpl_mat_cat_for_dvds():
    assert sierra2store.determine_bpl_mat_cat(
        'DVD', '41adv', '-') == 'dv'


def test_determine_bpl_mat_cat_for_cds():
    assert sierra2store.determine_bpl_mat_cat(
        'CD ORCH CHOPIN', '11acd', '-') == 'cd'


def test_determine_bpl_mat_cat_for_dewey_0xx():
    assert sierra2store.determine_bpl_mat_cat(
        '005.42 B', '40anf', '-') == 'd0'


def test_determine_bpl_mat_cat_for_dewey_1xx():
    assert sierra2store.determine_bpl_mat_cat(
        '158 B', '40anf', '-') == 'd1'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 158.12 B', '40awl', '-') == 'd1'


def test_determine_bpl_mat_cat_for_dewey_2xx():
    assert sierra2store.determine_bpl_mat_cat(
        '248 B', '40anf', '-') == 'd2'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 248.12 B', '40awl', '-') == 'd2'


def test_determine_bpl_mat_cat_for_dewey_3xx():
    assert sierra2store.determine_bpl_mat_cat(
        '364 B', '40anf', '-') == 'd3'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 355.12 B', '40awl', '-') == 'd3'


def test_determine_bpl_mat_cat_for_dewey_4xx():
    assert sierra2store.determine_bpl_mat_cat(
        '400 B', '40anf', '-') == 'd4'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 400 B', '40awl', '-') == 'd4'


def test_determine_bpl_mat_cat_for_dewey_5xx():
    assert sierra2store.determine_bpl_mat_cat(
        '500 B', '40anf', '-') == 'd5'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 500.092 B', '40awl', '-') == 'd5'


def test_determine_bpl_mat_cat_for_dewey_6xx():
    assert sierra2store.determine_bpl_mat_cat(
        '623.4 B', '40anf', '-') == 'd6'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 600.92 B', '40awl', '-') == 'd6'


def test_determine_bpl_mat_cat_for_dewey_7xx():
    assert sierra2store.determine_bpl_mat_cat(
        '700.092 B', '40anf', '-') == 'd7'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 700 B', '40awl', '-') == 'd7'


def test_determine_bpl_mat_cat_for_dewey_8xx():
    assert sierra2store.determine_bpl_mat_cat(
        '823.33 B K', '14anf', '-') == 'd8'
    assert sierra2store.determine_bpl_mat_cat(
        '823 B', '14anf', '-') == 'd8'


def test_determine_bpl_mat_cat_for_dewey_9xx():
    assert sierra2store.determine_bpl_mat_cat(
        '973 B', '40anf', '-') == 'd9'
    assert sierra2store.determine_bpl_mat_cat(
        'CHI 974.74 B', '40awl', '-') == 'd9'


def test_get_mat_cat_id_for_bpl_unknown_material():
    mat_cat_idx = {None: 1}
    assert sierra2store.get_mat_cat_id(
        '', '14', '-', 1, mat_cat_idx) == 1


def test_get_mat_cat_id_for_nyp_unknown_material():
    mat_cat_idx = {None: 1}
    assert sierra2store.get_mat_cat_id(
        '', 'mm', '-', 2, mat_cat_idx) == 1


def test_parse_shelfcode_positive():
    assert sierra2store.parse_shelfcode(
        '14anf') == 'nf'


def test_parse_shelfcode_when_missing():
    assert sierra2store.parse_shelfcode(
        '14') is None


def test_parse_shelfcode_when_none():
    assert sierra2store.parse_shelfcode(
        None) is None


def test_parse_shelfcode_when_empty_string():
    assert sierra2store.parse_shelfcode(
        '') is None
