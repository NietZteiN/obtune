import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string]) update, Nullable!(long[string]) starting) 
{
    if (!starting.isNull) {
        long[string] d = starting.get();
        if (!update.isNull) {
            foreach (key, value; update.get()) {
                if (key in d) {
                    d[key] += value;
                } else {
                    d[key] = value;
                }
            }
        }
        return Nullable!(long[string])(d);
    }
    return Nullable!(long[string]).init;
}

unittest
{
    alias candidate = f;

{
        auto result = candidate(Nullable!(long[string]).init, ["desciduous": 2L].nullable);
        assert(!result.isNull && result.get == ["desciduous": 2L]);
}

}
void main(){}
