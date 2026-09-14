import std.math;
import std.typecons;

long f(Nullable!(long[long]) d, long index) 
{
    if (!d.isNull) {
        auto map = d.get;
        auto length = map.length;
        auto idx = index % length;
        auto v = map[map.keys[0]];
        for (int i = 0; i < idx; ++i) {
            map.remove(map.keys[0]);
        }
        return v;
    }
    return 0;
}
unittest
{
    alias candidate = f;

    assert(candidate([27L: 39L].nullable, 1L) == 39L);
}
void main(){}
