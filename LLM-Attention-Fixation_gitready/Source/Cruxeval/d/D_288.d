import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.conv;
import std.string;

Tuple!(long, long)[] f(Nullable!(long[long]) d) 
{
    if (d.isNull) {
        return [];
    }

    auto dict = d.get();
    auto sorted_pairs = dict.byKeyValue.array.sort!((a, b) => 
        (a.key.to!string ~ a.value.to!string).length < (b.key.to!string ~ b.value.to!string).length
    );

    Tuple!(long, long)[] result;
    foreach (pair; sorted_pairs) {
        if (pair.key < pair.value) {
            result ~= tuple(pair.key, pair.value);
        }
    }
    return result;
}

unittest
{
    alias candidate = f;

    assert(candidate([55L: 4L, 4L: 555L, 1L: 3L, 99L: 21L, 499L: 4L, 71L: 7L, 12L: 6L].nullable) == [tuple(1L, 3L), tuple(4L, 555L)]);
}
void main(){}
