import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) d, long k) 
{
    if (!d.isNull) {
        long[long] new_d;
        foreach (key, value; d.get()) {
            if (key < k) {
                new_d[key] = value;
            }
        }
        return Nullable!(long[long])(new_d);
    }
    return Nullable!(long[long]).init;
}

unittest
{
    alias candidate = f;

{
        auto result = candidate([1L: 2L, 2L: 4L, 3L: 3L].nullable, 3L);
        assert(!result.isNull && result.get == [1L: 2L, 2L: 4L]);
}

}
void main(){}
