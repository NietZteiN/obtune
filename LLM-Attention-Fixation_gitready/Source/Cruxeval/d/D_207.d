import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string])[] commands) 
{
    long[string] d;
    foreach (c; commands)
    {
        foreach (key, value; c.get)
        {
            d[key] = value;
        }
    }
    return Nullable!(long[string])(d);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([["brown": 2L].nullable, ["blue": 5L].nullable, ["bright": 4L].nullable]);
        assert(!result.isNull && result.get == ["brown": 2L, "blue": 5L, "bright": 4L]);
}

}
void main(){}
