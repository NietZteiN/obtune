import std.math;
import std.typecons;
import std.array : empty;

Nullable!(long[long]) f(Nullable!(long[long]) cart) 
{
    if (!cart.isNull) {
        auto c = cart.get;
        while (c.length > 5) {
            c.remove(c.length-1);
        }
        return Nullable!(long[long])(c);
    }
    return Nullable!(long[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(Nullable!(long[long]).init);
        assert(result.isNull);
}

}
void main(){}
