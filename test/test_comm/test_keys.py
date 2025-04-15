import gedge
import pytest

from gedge.comm import keys

class TestSanity:
    def test_key_join(self):
        expected_key = "part0/part1/part2"
        assert expected_key == keys.key_join("part0", "part1", "part2")

    def test_node_key_prefix(self):
        expected_key = "prefix/NODE/name"
        assert expected_key == keys.node_key_prefix(prefix="prefix", name="name")

    def test_meta_key_prefix(self):
        expected_key = "prefix/NODE/name/META"
        assert expected_key == keys.meta_key_prefix(prefix="prefix", name="name")

    def test_tag_data_key_prefix(self):
        expected_key = "prefix/NODE/name/TAGS/DATA"
        assert expected_key == keys.tag_data_key_prefix(prefix="prefix", name="name")

    def test_tag_data_key(self):
        expected_key = "prefix/NODE/name/TAGS/DATA/key"

        assert expected_key == keys.tag_data_key(prefix="prefix", name="name", key="key")

    def test_tag_write_key_prefix(self):
        expected_key = "prefix/NODE/name/TAGS/WRITE"
        assert expected_key == keys.tag_write_key_prefix(prefix="prefix", name="name")

    def test_tag_write_key(self):
        expected_key = "prefix/NODE/name/TAGS/WRITE/key"
        assert expected_key == keys.tag_write_key(prefix="prefix", name="name", key="key")

    def test_state_key_prefix(self):
        expected_key = "prefix/NODE/name/STATE"
        assert expected_key == keys.state_key_prefix(prefix="prefix", name="name")

    def test_method_key_prefix(self):
        expected_key = "prefix/NODE/name/METHODS"
        assert expected_key == keys.method_key_prefix(prefix="prefix", name="name")

    def test_liveliness_key_prefix(self):
        expected_key = "prefix/NODE/name"
        assert expected_key == keys.liveliness_key_prefix(prefix="prefix", name="name")

    def test_subnodes_key_prefix(self):
        expected_key = "prefix/NODE/node_name/SUBNODES"
        assert expected_key == keys.subnodes_key_prefix(prefix="prefix", node_name="node_name")

    def test_method_response_from_call(self):
        expected_key = "key_expr/RESPONSE"
        assert expected_key == keys.method_response_from_call(key_expr="key_expr")

    def test_internal_to_user_key(self):
        node_key = keys.node_key_prefix(prefix="prefix", name="node")
        expected_key = "prefix/node"
        assert expected_key == keys.internal_to_user_key(key_expr=node_key)

class TestWhitespace:
    def test_key_join(self):
        expected_key = "    p   a   r  t 0/  p  a  r   t      1 /     par t    2"
        assert expected_key == keys.key_join("    p   a   r  t 0", "  p  a  r   t      1 ", "     par t    2")

    def test_node_key_prefix(self):
        expected_key = "p    re   f  i x/NODE/n    a    m      e"
        assert expected_key == keys.node_key_prefix(prefix="p    re   f  i x", name="n    a    m      e")

    def test_meta_key_prefix(self):
        expected_key = "p    re   f   i x/NODE/   n     a    m  e            /META"
        assert expected_key == keys.meta_key_prefix(prefix="p    re   f   i x", name="   n     a    m  e            ")
    
    def test_tag_data_key_prefix(self):
        expected_key = "p    r   e   f    ix/NODE/   n    a    m e /TAGS/DATA"
        assert expected_key == keys.tag_data_key_prefix(prefix="p    r   e   f    ix", name="   n    a    m e ")

    def test_tag_data_key(self):
        expected_key = "    p   r  e f      i x      /NODE/  n   a  m      e/TAGS/DATA/   k      e     y"
        assert expected_key == keys.tag_data_key(prefix="    p   r  e f      i x      ", name="  n   a  m      e", key="   k      e     y")

    def test_tag_write_key_prefix(self):
        expected_key = "    p   r  e    f  ix     /NODE/n     a   m   e/TAGS/WRITE"
        assert expected_key == keys.tag_write_key_prefix(prefix="    p   r  e    f  ix     ", name="n     a   m   e")

    def test_tag_write_key(self):
        expected_key = "p    r   e  f  i    x/NODE/n    a    m    e/TAGS/WRITE/     k   e  y    "
        assert expected_key == keys.tag_write_key(prefix="p    r   e  f  i    x", name="n    a    m    e", key="     k   e  y    ")

    def test_state_key_prefix(self):
        expected_key = "pr       e  f  i x   /NODE/   n  a m e     /STATE"
        assert expected_key == keys.state_key_prefix(prefix="pr       e  f  i x   ", name="   n  a m e     ")

    def test_method_key_prefix(self):
        expected_key = "     p r  e    f    i    x/NODE/       n     a    m e     /METHODS"
        assert expected_key == keys.method_key_prefix(prefix="     p r  e    f    i    x", name="       n     a    m e     ")

    def test_liveliness_key_prefix(self):
        expected_key = "p     r     e    f    i     x/NODE/      n   a   m e  " 
        assert expected_key == keys.liveliness_key_prefix(prefix="p     r     e    f    i     x", name="      n   a   m e  ")

    def test_subnodes_key_prefix(self):
        expected_key = "    p  r e        f   i   x      /NODE/    n  o d e _       n  a m e  /SUBNODES"
        assert expected_key == keys.subnodes_key_prefix(prefix="    p  r e        f   i   x      ", node_name="    n  o d e _       n  a m e  ")

    def test_method_response_from_call(self):
        expected_key = "     k    e  y      _    e  x p r   /RESPONSE"
        assert expected_key == keys.method_response_from_call(key_expr="     k    e  y      _    e  x p r   ")

    def test_internal_to_user_key(self):
        node_key = keys.node_key_prefix(prefix="     p    r    e   f   i  x     ", name="     n    o d    e     ")
        expected_key = "     p    r    e   f   i  x     /     n    o d    e     "
        assert expected_key == keys.internal_to_user_key(key_expr=node_key)

class TestEmpty:
    def test_key_join(self):
        assert '' == keys.key_join()

    def test_node_key_prefix(self):
        expected_key = "/NODE/"
        assert  expected_key == keys.node_key_prefix(prefix="", name="")

    def test_meta_key_prefix(self):
        expected_key = "/NODE//META"
        assert expected_key == keys.meta_key_prefix(prefix="", name="")

    def test_tag_data_key_prefix(self):
        expected_key = "/NODE//TAGS/DATA"
        assert expected_key == keys.tag_data_key_prefix(prefix="", name="")

    def test_tag_data_key(self):
        expected_key = "/NODE//TAGS/DATA/"
        assert expected_key == keys.tag_data_key(prefix="", name="", key="")

    def test_tag_write_key_prefix(self):
        expected_key = "/NODE//TAGS/WRITE"
        assert expected_key == keys.tag_write_key_prefix(prefix="", name="")

    def test_tag_write_key(self):
        expected_key = "/NODE//TAGS/WRITE/"
        assert expected_key == keys.tag_write_key(prefix="", name="", key="")

    def test_state_key_prefix(self):
        expected_key = "/NODE//STATE"
        assert expected_key == keys.state_key_prefix(prefix="", name="")

    def test_method_key_prefix_empty_param(self):
        expected_key = "/NODE//METHODS"
        assert expected_key == keys.method_key_prefix(prefix="", name="")

    def test_liveliness_key_prefix(self):
        expected_key = "/NODE/"
        assert expected_key == keys.liveliness_key_prefix(prefix="", name="")

    def test_subnodes_key_prefix(self):
        expected_key = "/NODE//SUBNODES"
        assert expected_key == keys.subnodes_key_prefix(prefix="", node_name="")

    def test_method_response_from_call(self):
        expected_key = "/RESPONSE"
        assert expected_key == keys.method_response_from_call(key_expr="")

    def test_internal_to_user_key(self):
        with pytest.raises(ValueError, match="'NODE' is not in list"):
            keys.internal_to_user_key(key_expr="")

class TestUnicode:
    UnicodeChars = [
        ("préfix", "名", "🔑"),
        ("ø", "ç", "🔥"),
        ("שלום", "мир", "🚀"),
        ("ひらがな", "العالم", "📦"),
        ("✓", "∞", "§"),
    ]

    ids = [
        "Latin-CJK-Emoji",
        "Scandinavian-LatinSymbol-Fire",
        "Hebrew-Cyrillic-Rocket",
        "Japanese-Arabic-Package",
        "Check-Infinity-Section"
    ]

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_key_join(self, prefix, name, key):
        expected_key = f"{prefix}/{name}/{key}"
        assert expected_key == keys.key_join(prefix, name, key)

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_node_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}"

        assert expected_key == keys.node_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_meta_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}/META"
    
        assert expected_key == keys.meta_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_tag_data_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}/TAGS/DATA"
    
        assert expected_key == keys.tag_data_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_tag_data_key(seself, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/TAGS/DATA/{key}"

        assert expected_key == keys.tag_data_key(prefix=prefix, name=name, key=key)

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_tag_write_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}/TAGS/WRITE"
        assert expected_key == keys.tag_write_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_tag_write_key(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/TAGS/WRITE/{key}"
        assert expected_key == keys.tag_write_key(prefix=prefix, name=name, key=key)

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_state_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}/STATE"
        assert expected_key == keys.state_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_method_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}/METHODS"
        assert expected_key == keys.method_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_liveliness_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}"
        assert expected_key == keys.liveliness_key_prefix(prefix=prefix, name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_subnodes_key_prefix(self, prefix, name, key):
        expected_key = f"{prefix}/NODE/{name}/{key}/SUBNODES"
        assert expected_key == keys.subnodes_key_prefix(prefix=prefix, node_name=f"{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_method_response_from_call(self, prefix, name, key):
        expected_key = f"{prefix}/{name}/{key}/RESPONSE"
        assert expected_key == keys.method_response_from_call(key_expr=f"{prefix}/{name}/{key}")

    @pytest.mark.parametrize("prefix, name, key", UnicodeChars, ids=ids)
    def test_internal_to_user_key(self, prefix, name, key):
        node_key = keys.node_key_prefix(prefix=prefix, name=name)
        expected_key = f"{prefix}/{name}"
        assert expected_key == keys.internal_to_user_key(key_expr=node_key)

class TestOverlap:
    def test_overlap_one_wildcard_true(self):
        assert keys.overlap(key1="*/NODE/name", key2="*/NODE/name") == True

    def test_overlap_more_than_one_wildcard_true(self):
        assert keys.overlap(key1="*/*/name", key2="prefix/*/name") == True

    def test_overlap_more_than_all_wildcards_true(self):
        assert keys.overlap(key1="*/*/*", key2="prefix/NODE/name") == True

    def test_overlap_length_diff(self):
        assert keys.overlap(key1="1/2/3", key2="1/2") == False

    def test_overlap_component_diff(self):
        assert keys.overlap(key1="a/*/c", key2="a/*/d") == False

    def test_overlaps_multiple_wildcards(self):
        assert keys.overlap(key1="a/*/c", key2="a/b/*") == True